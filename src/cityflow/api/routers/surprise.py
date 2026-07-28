"""Q4 — AMS: số bất ngờ (mô-men bậc 2) của phân phối khu vực đón."""

from __future__ import annotations

from fastapi import APIRouter

from ..state import state

router = APIRouter()


@router.get("/surprise")
def surprise() -> dict:
    """Số bất ngờ tích lũy.

    ⚠️ docs/07_KET_QUA_E5_E6.md §9: ở phạm vi toàn cục, tín hiệu này YẾU (2,7× sau
    chuẩn hóa n^2) vì phân phối khu vực NYC khá đều. Dùng như chỉ báo phụ, không
    phải cơ chế phát hiện ùn tắc chính — xem /api/rules cho tín hiệu chính (Q6).
    """
    reg = state.registry
    return {
        "estimated": reg.surprise_number(),
        "n_events_seen": reg.zone_moment.n,
        "params": {"k": reg.cfg.ams_k},
        "note": "Tín hiệu yếu ở phạm vi toàn cục — xem /api/rules cho phát hiện chính",
        "memory_bytes": reg.zone_moment.memory_bytes(),
    }
