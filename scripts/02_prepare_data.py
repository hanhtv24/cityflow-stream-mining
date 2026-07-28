"""Phase 5 — Bước 2: Data Preparation (tầng L0).

Biến parquet thô của TLC thành luồng sự kiện đã chuẩn hóa và SẮP THEO THỜI GIAN.

Bước sắp xếp là BẮT BUỘC, không phải tối ưu hóa: Data Understanding đo được
44,67% bản ghi lệch thứ tự thời gian theo thứ tự file. Nếu nạp thẳng vào sketch,
bất biến của DGIM ("bucket mới nhỏ hơn bucket cũ hơn") bị phá vỡ và mọi kết quả
sẽ sai mà không có dấu hiệu báo lỗi.

Xem docs/04_DATA_UNDERSTANDING.md §3.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import PROCESSED_DIR, RAW_DIR  # noqa: E402

# Ngưỡng "chuyến giá cao" = phân vị 95 đo được trên FHVHV 2024-01.
HIGH_FARE_THRESHOLD = 68.52

# Ngưỡng "chuyến dài" (giây).
LONG_TRIP_SECONDS = 1800

REVENUE_CLIP = 255  # tương ứng m = 8 bit


def build_query(src: Path) -> str:
    return f"""
    SELECT
        pickup_datetime,
        CAST(PULocationID AS USMALLINT) AS pu_zone,
        -- Gộp 264 (N/A) và 265 (Unknown) thành một luồng 'unknown' duy nhất là 265.
        -- Không loại bỏ: 3,77% chuyến có DOLocationID unknown, loại đi sẽ làm lệch
        -- ground truth của mọi ước lượng liên quan khu vực trả.
        CAST(CASE WHEN DOLocationID = 264 THEN 265 ELSE DOLocationID END AS USMALLINT) AS do_zone,

        -- Doanh thu: FHVHV không có cột total_amount sẵn như Yellow Taxi.
        -- Kẹp sàn về 0: có 167 bản ghi âm (hoàn tiền/điều chỉnh).
        GREATEST(base_passenger_fare + tips + tolls, 0) AS revenue,

        -- Giá trị nguyên đã kẹp trần cho DGIM số nguyên (m = 8 bit -> 0..255).
        CAST(LEAST(ROUND(GREATEST(base_passenger_fare + tips + tolls, 0)), {REVENUE_CLIP})
             AS UTINYINT) AS revenue_int,

        -- Cờ đánh dấu bản ghi bị kẹp trần, để báo cáo tỷ lệ kẹp.
        (GREATEST(base_passenger_fare + tips + tolls, 0) > {REVENUE_CLIP}) AS revenue_clipped,

        -- Các vị từ luồng toàn cục.
        (PULocationID IN (1, 132, 138) OR DOLocationID IN (1, 132, 138)) AS is_airport,
        (trip_time > {LONG_TRIP_SECONDS})                                AS is_long_trip,
        (congestion_surcharge > 0)                                       AS has_congestion,
        (shared_request_flag = 'Y')                                      AS is_shared,
        (GREATEST(base_passenger_fare + tips + tolls, 0) > {HIGH_FARE_THRESHOLD}) AS is_high_fare

    FROM read_parquet('{src.as_posix()}')
    WHERE dropoff_datetime > pickup_datetime      -- loại 2 bản ghi sai thứ tự
      AND trip_time > 0                           -- loại 2 bản ghi thời lượng 0
      AND PULocationID BETWEEN 1 AND 265
      AND DOLocationID BETWEEN 1 AND 265
    ORDER BY pickup_datetime                      -- BƯỚC BẮT BUỘC (xem docstring)
    """


def prepare(month: str) -> None:
    src = RAW_DIR / f"fhvhv_tripdata_{month}.parquet"
    dst = PROCESSED_DIR / f"events_{month}.parquet"

    if not src.exists():
        raise FileNotFoundError(f"Không tìm thấy {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    t0 = time.perf_counter()

    n_raw = con.execute(f"SELECT count(*) FROM read_parquet('{src.as_posix()}')").fetchone()[0]
    print(f"  Đầu vào : {n_raw:,} bản ghi")

    con.execute(
        f"COPY ({build_query(src)}) TO '{dst.as_posix()}' "
        f"(FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    elapsed = time.perf_counter() - t0

    # --- Kiểm chứng kết quả ---
    stats = con.execute(f"""
        SELECT count(*)                                  AS n,
               sum(CAST(revenue_clipped AS INT))         AS n_clipped,
               sum(CAST(is_airport AS INT))              AS n_airport,
               sum(CAST(is_long_trip AS INT))            AS n_long,
               sum(CAST(has_congestion AS INT))          AS n_congestion,
               sum(CAST(is_shared AS INT))               AS n_shared,
               sum(CAST(is_high_fare AS INT))            AS n_high_fare
        FROM read_parquet('{dst.as_posix()}')
    """).fetchdf().iloc[0]

    n = int(stats["n"])
    print(f"  Đầu ra  : {n:,} bản ghi  (loại {n_raw - n:,})")
    print(f"  Thời gian: {elapsed:.1f}s  |  Kích thước: {dst.stat().st_size / 1e6:.1f} MB")

    # Xác minh thứ tự thời gian ĐÃ ĐÚNG — đây là lý do tồn tại của script này.
    ooo = con.execute(f"""
        WITH seq AS (
            SELECT pickup_datetime,
                   lag(pickup_datetime) OVER (ORDER BY rowid) AS prev
            FROM (SELECT pickup_datetime, row_number() OVER () AS rowid
                  FROM read_parquet('{dst.as_posix()}'))
        )
        SELECT count(*) FROM seq WHERE prev IS NOT NULL AND pickup_datetime < prev
    """).fetchone()[0]

    print(f"\n  Kiểm chứng thứ tự thời gian: {ooo:,} bản ghi lệch")
    if ooo != 0:
        raise RuntimeError(f"SẮP XẾP THẤT BẠI: còn {ooo:,} bản ghi lệch thứ tự")
    print("  -> ĐẠT: luồng đã được sắp đúng thứ tự sự kiện")

    print(f"\n  Tỷ lệ các vị từ luồng toàn cục:")
    for label, key in [("Sân bay", "n_airport"), ("Chuyến dài (>30ph)", "n_long"),
                       ("Phụ phí ùn tắc", "n_congestion"), ("Đi chung", "n_shared"),
                       ("Giá cao (>p95)", "n_high_fare")]:
        v = int(stats[key])
        print(f"      {label:22s} {v:>10,}  ({100 * v / n:5.2f}%)")

    v = int(stats["n_clipped"])
    print(f"      {'Bị kẹp trần (>255$)':22s} {v:>10,}  ({100 * v / n:5.3f}%)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default="2024-01", help="YYYY-MM")
    args = ap.parse_args()
    print(f"Chuẩn bị dữ liệu tháng {args.month}\n")
    prepare(args.month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
