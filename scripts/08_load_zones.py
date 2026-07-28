"""Nạp danh mục 265 khu vực (taxi_zone_lookup.csv + taxi_zones.geojson) vào PostgreSQL.

Chạy sau khi `docker compose up -d db` và trước khi khởi động API.
"""

from __future__ import annotations

import csv
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import AIRPORT_ZONES, REFERENCE_DIR  # noqa: E402
from cityflow.db.models import zones  # noqa: E402
from cityflow.db.session import get_engine  # noqa: E402


def load_geometries() -> dict[int, dict]:
    """Đọc taxi_zones.zip (shapefile) nếu có shapely+pyshp, ngược lại bỏ qua.

    GeoJSON là tiện ích cho bản đồ nhiệt trên dashboard, không phải yêu cầu bắt
    buộc của tầng dữ liệu — hệ thống vẫn hoạt động đầy đủ nếu bước này bị bỏ qua.
    """
    zip_path = REFERENCE_DIR / "taxi_zones.zip"
    if not zip_path.exists():
        return {}
    try:
        import shapefile  # pyshp
    except ImportError:
        print("  (bỏ qua hình học: chưa cài pyshp — `pip install pyshp`)")
        return {}

    extract_dir = REFERENCE_DIR / "_taxi_zones_extracted"
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        shp = next(n for n in names if n.endswith(".shp"))
        dbf = next(n for n in names if n.endswith(".dbf"))
        zf.extractall(extract_dir)

    # Giữ nguyên đường dẫn tương đối trong zip (VD "taxi_zones/taxi_zones.shp") —
    # dùng Path(...).name sẽ làm mất thư mục con và trỏ sai file.
    sf = shapefile.Reader(
        shp=str(extract_dir / shp),
        dbf=str(extract_dir / dbf),
    )
    geoms = {}
    for sr in sf.shapeRecords():
        loc_id = int(sr.record["LocationID"])
        geoms[loc_id] = sr.shape.__geo_interface__
    return geoms


def main() -> int:
    lookup_path = REFERENCE_DIR / "taxi_zone_lookup.csv"
    if not lookup_path.exists():
        print(f"Không tìm thấy {lookup_path}. Chạy scripts/download_data.py trước.")
        return 1

    geoms = load_geometries()
    rows = []
    with open(lookup_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            loc_id = int(row["LocationID"])
            rows.append({
                "location_id": loc_id,
                "borough": row["Borough"],
                "zone_name": row["Zone"],
                "service_zone": row.get("service_zone"),
                "is_airport": loc_id in AIRPORT_ZONES,
                "geometry": json.dumps(geoms[loc_id]) if loc_id in geoms else None,
            })

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(zones.delete())
        conn.execute(zones.insert(), rows)

    print(f"Đã nạp {len(rows)} khu vực"
          f"{' kèm hình học' if geoms else ' (không có hình học)'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
