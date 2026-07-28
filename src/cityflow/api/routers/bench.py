"""Kết quả thực nghiệm E1-E11 — dùng cho màn hình Benchmark Dashboard.

Đọc trực tiếp các file JSON đã sinh ra ở Phase 5 (docs/*.json) thay vì tính lại —
đây LÀ kết quả benchmark chính thức của đồ án, không phải dữ liệu demo.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from ...config import DOCS_DIR

router = APIRouter()

_FILES = {
    "E1_E3": "e1_e3_results.json",
    "E4": "e4_h1_results.json",
    "E5_E6": "e5_e6_results.json",
    "E7": "e7_results.json",
    "E9_E11": "e9_e11_results.json",
}


@router.get("/bench/{experiment}")
def get_benchmark(experiment: str) -> dict:
    key = experiment.upper()
    if key not in _FILES:
        raise HTTPException(404, f"Không rõ thực nghiệm '{experiment}'. "
                                 f"Chọn: {list(_FILES)}")
    path = DOCS_DIR / _FILES[key]
    if not path.exists():
        raise HTTPException(404, f"Chưa có kết quả cho {key} — chạy script tương ứng trước")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/bench")
def list_benchmarks() -> dict:
    return {
        "available": [k for k, v in _FILES.items() if (DOCS_DIR / v).exists()],
        "all": list(_FILES),
    }
