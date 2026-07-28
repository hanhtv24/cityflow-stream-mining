"""Phase 5 — Bước 1: Xác minh rủi ro R1 (Data Understanding).

Mục tiêu: xác minh mọi giả định về dữ liệu đã nêu ở Phase 4 §2 bằng số liệu thật,
TRƯỚC khi viết bất kỳ dòng mã thuật toán nào.

Checklist (Phase 4 §2.3):
  1. Số bản ghi thật vs ước tính (~18-20 triệu/tháng)
  2. Lược đồ cột thật vs kỳ vọng
  3. Giá trị thiếu theo cột
  4. Tính hợp lệ: dropoff > pickup, trip_miles > 0, LocationID trong [1,265]
  5. Phân phối chuyến theo giờ/ngày/khu vực -> tính phi dừng
  6. Tỷ lệ LocationID 264/265 (Unknown/NV)
  7. Sự kiện lệch thứ tự thời gian (out-of-order)
  8. Phân phối total_amount -> chốt số bit m cho DGIM số nguyên
  9. Xác minh LocationID của sân bay
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import RAW_DIR, REFERENCE_DIR  # noqa: E402

FHVHV = RAW_DIR / "fhvhv_tripdata_2024-01.parquet"
YELLOW = RAW_DIR / "yellow_tripdata_2024-01.parquet"
ZONES = REFERENCE_DIR / "taxi_zone_lookup.csv"

OUT = Path(__file__).resolve().parents[1] / "docs" / "data_understanding_results.json"

results: dict = {}


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def main() -> int:
    con = duckdb.connect()

    # --- 1. Lược đồ và quy mô ---------------------------------------------
    section("1. LƯỢC ĐỒ VÀ QUY MÔ")

    for label, path in [("FHVHV", FHVHV), ("YELLOW", YELLOW)]:
        if not path.exists():
            print(f"  {label}: KHÔNG TỒN TẠI {path}")
            continue
        schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path.as_posix()}')").fetchall()
        n = con.execute(f"SELECT count(*) FROM read_parquet('{path.as_posix()}')").fetchone()[0]
        size_mb = path.stat().st_size / 1e6
        print(f"\n  {label}: {n:,} bản ghi | {size_mb:.1f} MB | {len(schema)} cột")
        for col, dtype, *_ in schema:
            print(f"      {col:28s} {dtype}")
        results[f"{label.lower()}_rows"] = n
        results[f"{label.lower()}_columns"] = [c[0] for c in schema]
        results[f"{label.lower()}_size_mb"] = round(size_mb, 1)

    fhv = f"read_parquet('{FHVHV.as_posix()}')"

    # --- 2. Danh mục khu vực ----------------------------------------------
    section("2. DANH MỤC KHU VỰC")
    zdf = con.execute(f"SELECT * FROM read_csv_auto('{ZONES.as_posix()}')").fetchdf()
    print(f"  Số khu vực: {len(zdf)}")
    print(f"  Cột: {list(zdf.columns)}")
    print(f"\n  Phân bố theo Borough:")
    for borough, cnt in zdf["Borough"].value_counts().items():
        print(f"      {borough:16s} {cnt:4d}")

    print(f"\n  Khu vực sân bay (tìm theo tên):")
    airports = zdf[zdf["Zone"].str.contains("Airport", case=False, na=False)]
    for _, row in airports.iterrows():
        print(f"      LocationID {row['LocationID']:4d}  {row['Zone']}  ({row['Borough']})")
    results["airport_zones"] = airports["LocationID"].tolist()

    print(f"\n  Khu vực Unknown/N.A.:")
    # Khớp theo cột Borough, không theo tên Zone: dùng regex trên tên Zone sẽ khớp nhầm
    # (dấu chấm trong "N.A" là ký tự đại diện, khớp cả "Auburndale", "Glendale"...).
    unknown = zdf[zdf["Borough"].isin(["Unknown", "N/A"])]
    for _, row in unknown.iterrows():
        print(f"      LocationID {row['LocationID']:4d}  {row['Zone']}  ({row['Borough']})")
    results["unknown_zones"] = unknown["LocationID"].tolist()
    results["n_zones"] = len(zdf)

    # --- 3. Giá trị thiếu -------------------------------------------------
    section("3. GIÁ TRỊ THIẾU (các cột CityFlow sử dụng)")
    cols = ["pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID",
            "trip_miles", "trip_time", "base_passenger_fare", "tips", "tolls",
            "congestion_surcharge", "shared_request_flag"]
    available = set(results.get("fhvhv_columns", []))
    checks = [f"sum(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) AS {c}"
              for c in cols if c in available]
    missing_cols = [c for c in cols if c not in available]
    if missing_cols:
        print(f"  ⚠️  Cột KHÔNG TỒN TẠI trong dữ liệu: {missing_cols}")
    row = con.execute(f"SELECT {', '.join(checks)} FROM {fhv}").fetchdf().iloc[0]
    total = results["fhvhv_rows"]
    for col, nulls in row.items():
        pct = 100 * nulls / total
        flag = " ⚠️" if pct > 1 else ""
        print(f"      {col:24s} {int(nulls):>10,}  ({pct:5.2f}%){flag}")
    results["null_counts"] = {k: int(v) for k, v in row.items()}
    results["missing_expected_columns"] = missing_cols

    # --- 4. Tính hợp lệ ---------------------------------------------------
    section("4. TÍNH HỢP LỆ")
    valid = con.execute(f"""
        SELECT
            sum(CASE WHEN dropoff_datetime <= pickup_datetime THEN 1 ELSE 0 END) AS bad_time_order,
            sum(CASE WHEN trip_miles <= 0 THEN 1 ELSE 0 END)                     AS zero_miles,
            sum(CASE WHEN trip_time <= 0 THEN 1 ELSE 0 END)                      AS zero_time,
            sum(CASE WHEN PULocationID NOT BETWEEN 1 AND 265 THEN 1 ELSE 0 END)  AS bad_pu,
            sum(CASE WHEN DOLocationID NOT BETWEEN 1 AND 265 THEN 1 ELSE 0 END)  AS bad_do,
            sum(CASE WHEN PULocationID IN (264,265) THEN 1 ELSE 0 END)           AS unknown_pu,
            sum(CASE WHEN DOLocationID IN (264,265) THEN 1 ELSE 0 END)           AS unknown_do,
            min(pickup_datetime) AS min_pickup,
            max(pickup_datetime) AS max_pickup
        FROM {fhv}
    """).fetchdf().iloc[0]
    for k, v in valid.items():
        if "pickup" in k:
            print(f"      {k:20s} {v}")
        else:
            print(f"      {k:20s} {int(v):>10,}  ({100*v/total:5.2f}%)")
    results["validity"] = {k: (str(v) if "pickup" in k else int(v)) for k, v in valid.items()}

    # --- 5. Sự kiện lệch thứ tự thời gian ---------------------------------
    section("5. SỰ KIỆN LỆCH THỨ TỰ (ảnh hưởng thiết kế replay)")
    ooo = con.execute(f"""
        WITH seq AS (
            SELECT pickup_datetime,
                   lag(pickup_datetime) OVER (ORDER BY rowid) AS prev
            FROM (SELECT pickup_datetime, row_number() OVER () AS rowid FROM {fhv})
        )
        SELECT count(*) AS out_of_order FROM seq WHERE prev IS NOT NULL AND pickup_datetime < prev
    """).fetchone()[0]
    print(f"      Bản ghi lệch thứ tự theo thứ tự file: {ooo:,} ({100*ooo/total:.2f}%)")
    print(f"      -> {'CẦN sắp xếp lại' if ooo > 0 else 'File đã sắp sẵn'} trước khi replay")
    results["out_of_order"] = int(ooo)

    # --- 6. Phân phối doanh thu -> chốt m cho DGIM số nguyên --------------
    section("6. PHÂN PHỐI DOANH THU (chốt tham số m cho DGIM số nguyên)")
    fare = con.execute(f"""
        SELECT
            min(total)  AS min_v, max(total) AS max_v, avg(total) AS mean_v,
            quantile_cont(total, 0.50) AS p50, quantile_cont(total, 0.95) AS p95,
            quantile_cont(total, 0.99) AS p99, quantile_cont(total, 0.999) AS p999,
            sum(CASE WHEN total < 0 THEN 1 ELSE 0 END) AS negative_cnt
        FROM (SELECT base_passenger_fare + COALESCE(tips,0) + COALESCE(tolls,0) AS total FROM {fhv})
    """).fetchdf().iloc[0]
    for k, v in fare.items():
        print(f"      {k:14s} {v:>14,.2f}")
    p999 = float(fare["p999"])
    max_v = float(fare["max_v"])
    import math
    m_p999 = math.ceil(math.log2(max(p999, 1) + 1))
    m_max = math.ceil(math.log2(max(max_v, 1) + 1))
    print(f"\n      Số bit cần cho p99.9 ({p999:.0f} USD): m = {m_p999}")
    print(f"      Số bit cần cho max   ({max_v:.0f} USD): m = {m_max}")
    print(f"      -> Khuyến nghị m = {m_p999} kèm kẹp trần (clipping), ghi nhận tỷ lệ bị kẹp")
    results["fare"] = {k: float(v) for k, v in fare.items()}
    results["recommended_m"] = m_p999

    # --- 7. Phân phối theo khu vực ----------------------------------------
    section("7. PHÂN PHỐI THEO KHU VỰC (kiểm tra độ lệch)")
    zone_dist = con.execute(f"""
        SELECT PULocationID, count(*) AS n
        FROM {fhv} GROUP BY PULocationID ORDER BY n DESC
    """).fetchdf()
    top10 = zone_dist.head(10)
    print(f"      Số khu vực đón phân biệt: {len(zone_dist)}")
    print(f"      Top 10 khu vực đón:")
    zmap = dict(zip(zdf["LocationID"], zdf["Zone"]))
    for _, r in top10.iterrows():
        zid = int(r["PULocationID"])
        print(f"          {zid:4d} {zmap.get(zid,'?')[:32]:34s} {int(r['n']):>9,}  ({100*r['n']/total:5.2f}%)")
    top10_share = 100 * top10["n"].sum() / total
    print(f"\n      Top 10 chiếm {top10_share:.1f}% tổng số chuyến")
    print(f"      -> {'Phân phối LỆCH mạnh' if top10_share > 30 else 'Phân phối tương đối đều'}")
    results["n_distinct_pu_zones"] = len(zone_dist)
    results["top10_zone_share_pct"] = round(float(top10_share), 2)

    # --- 8. Tính phi dừng theo giờ ----------------------------------------
    section("8. TÍNH PHI DỪNG (phân phối theo giờ trong ngày)")
    hourly = con.execute(f"""
        SELECT hour(pickup_datetime) AS h, count(*) AS n
        FROM {fhv} GROUP BY h ORDER BY h
    """).fetchdf()
    mx, mn = int(hourly["n"].max()), int(hourly["n"].min())
    print(f"      Giờ cao điểm nhất: {int(hourly.loc[hourly['n'].idxmax(),'h']):2d}h  {mx:>9,} chuyến")
    print(f"      Giờ thấp nhất:     {int(hourly.loc[hourly['n'].idxmin(),'h']):2d}h  {mn:>9,} chuyến")
    print(f"      Tỷ lệ cao/thấp: {mx/mn:.1f}x  -> xác nhận luồng PHI DỪNG (slide tr.7)")
    for _, r in hourly.iterrows():
        bar = "#" * int(60 * r["n"] / mx)
        print(f"          {int(r['h']):02d}h {int(r['n']):>9,} {bar}")
    results["hourly_peak_ratio"] = round(mx / mn, 2)

    # --- 9. Số tuyến phân biệt (ground truth cho FM) ----------------------
    section("9. SỐ TUYẾN PHÂN BIỆT (ground truth cho Flajolet-Martin)")
    routes = con.execute(f"""
        SELECT count(DISTINCT PULocationID * 1000 + DOLocationID) FROM {fhv}
    """).fetchone()[0]
    print(f"      Số cặp (đón, trả) phân biệt: {routes:,}  (tối đa lý thuyết 265^2 = 70,225)")
    results["distinct_routes"] = int(routes)

    # --- Lưu kết quả ------------------------------------------------------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
