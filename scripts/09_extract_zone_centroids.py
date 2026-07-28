"""Trích tọa độ trung tâm (centroid) của 265 khu vực taxi cho bản đồ nhiệt.

Shapefile TLC dùng hệ tọa độ NAD83 State Plane New York (EPSG:2263, đơn vị feet),
cần chuyển sang WGS84 (EPSG:4326, lat/lon) để hiển thị trên Leaflet.

Centroid tính xấp xỉ bằng trung bình các đỉnh đa giác — đủ chính xác cho việc đặt
điểm trên bản đồ nhiệt, không dùng cho phân tích không gian chính xác.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import shapefile
from pyproj import Transformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import REFERENCE_DIR  # noqa: E402

WEB_PUBLIC = Path(__file__).resolve().parents[1] / "web" / "public"


def main() -> int:
    extract_dir = REFERENCE_DIR / "_extracted"
    with zipfile.ZipFile(REFERENCE_DIR / "taxi_zones.zip") as zf:
        zf.extractall(extract_dir)

    sf = shapefile.Reader(str(extract_dir / "taxi_zones" / "taxi_zones.shp"))
    transformer = Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)

    zones: dict[int, list[float]] = {}
    for sr in sf.shapeRecords():
        loc_id = int(sr.record["LocationID"])
        pts = sr.shape.points
        if not pts:
            continue
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        lon, lat = transformer.transform(cx, cy)
        zones[loc_id] = [round(lat, 5), round(lon, 5)]

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)
    (WEB_PUBLIC / "zone_centroids.json").write_text(
        json.dumps(zones), encoding="utf-8"
    )
    print(f"Đã lưu {len(zones)} centroid vào {WEB_PUBLIC / 'zone_centroids.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
