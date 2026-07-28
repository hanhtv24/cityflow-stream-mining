"""Tải dữ liệu NYC TLC Trip Records.

Dữ liệu thô được lưu NGOÀI thư mục OneDrive để tránh đồng bộ hàng trăm MB.
Đường dẫn cấu hình qua biến môi trường CITYFLOW_DATA_DIR.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

BASE = "https://d37ci6vzurychx.cloudfront.net"
DATA_DIR = Path(os.environ.get("CITYFLOW_DATA_DIR", r"C:\Users\leotran\cityflow_data"))

FILES = [
    ("reference", "taxi_zone_lookup.csv", f"{BASE}/misc/taxi_zone_lookup.csv"),
    ("reference", "taxi_zones.zip", f"{BASE}/misc/taxi_zones.zip"),
    ("raw", "yellow_tripdata_2024-01.parquet", f"{BASE}/trip-data/yellow_tripdata_2024-01.parquet"),
    ("raw", "fhvhv_tripdata_2024-01.parquet", f"{BASE}/trip-data/fhvhv_tripdata_2024-01.parquet"),
]


def download(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"  [bỏ qua] {dest.name} đã tồn tại ({dest.stat().st_size / 1e6:.1f} MB)")
        return

    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                done += len(chunk)
                if total:
                    pct = 100 * done / total
                    print(f"\r  {dest.name}: {done/1e6:7.1f}/{total/1e6:.1f} MB ({pct:5.1f}%)",
                          end="", flush=True)
    tmp.rename(dest)
    print(f"\r  [xong]  {dest.name}: {dest.stat().st_size / 1e6:.1f} MB" + " " * 20)


def main() -> int:
    for sub, name, url in FILES:
        target_dir = DATA_DIR / sub
        target_dir.mkdir(parents=True, exist_ok=True)
        download(url, target_dir / name)
    print(f"\nDữ liệu đã lưu tại: {DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
