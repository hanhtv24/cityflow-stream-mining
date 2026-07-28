"""Q3 — Flajolet-Martin: số tuyến phân biệt."""

from __future__ import annotations

from fastapi import APIRouter

from ..state import state

router = APIRouter()


@router.get("/distinct/routes")
def distinct_routes() -> dict:
    """Số tuyến (cặp đón-trả) phân biệt, cả luồng đã thấy tới nay.

    Cấu hình m=256 (E5): sai số trung vị 6,4%, p90 10,6% — dưới cận 11,2% của
    ước lượng 2^R đơn lẻ. Xem docs/07_KET_QUA_E5_E6.md.
    """
    reg = state.registry
    return {
        "estimated": round(reg.distinct_routes()),
        "params": {"m": reg.cfg.fm_m, "strategy": "loglog_calibrated"},
        "theoretical_error_median": 0.064,
        "memory_bytes": reg.routes.memory_bytes(),
    }
