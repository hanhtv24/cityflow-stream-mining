"""Q1, Q2 — truy vấn cửa sổ trượt: đếm bit 1 (DGIM) và tổng số nguyên (DGIM-Integer)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..state import state

router = APIRouter()

THEORETICAL_BOUND_50PCT = 0.5
"""Cận sai số r=2 (slide tr.64). Registry vận hành ở r=8 (E2), sai số thực tế
đo được thấp hơn nhiều — xem docs/05_KET_QUA_E1_E3.md."""


@router.get("/window/count")
def window_count(
    zone: int = Query(..., ge=1, le=265, description="LocationID, 1..265"),
    direction: str = Query("pickup", pattern="^(pickup|dropoff)$"),
    k: int | None = Query(None, description="Cửa sổ, mặc định N của registry"),
) -> dict:
    """Q1 — DGIM: số chuyến trong k sự kiện gần nhất tại khu vực `zone`."""
    reg = state.registry
    if zone not in reg.pu_streams:
        raise HTTPException(404, f"Không có khu vực {zone}")

    k = k or reg.cfg.N
    estimate = (reg.count_pickups(zone, k) if direction == "pickup"
               else reg.count_dropoffs(zone, k))

    return {
        "zone": zone, "zone_name": state.zone_names.get(zone, "?"),
        "direction": direction, "k": k, "estimated": estimate,
        "theoretical_bound": THEORETICAL_BOUND_50PCT,
        "params": {"N": reg.cfg.N, "r": reg.cfg.dgim_r},
        "memory_bytes": (reg.pu_streams if direction == "pickup"
                         else reg.do_streams)[zone].memory_bytes(),
    }


@router.get("/window/sum")
def window_sum(k: int | None = Query(None)) -> dict:
    """Q2 — DGIM mở rộng cho số nguyên: tổng doanh thu trong k sự kiện gần nhất."""
    reg = state.registry
    k = k or reg.cfg.N
    estimate = reg.total_revenue(k)
    per_bit = reg.revenue.query_per_bit(k, reg.now)

    return {
        "k": k, "estimated_usd": estimate,
        "per_bit_estimates": per_bit,
        "params": {"N": reg.cfg.N, "m": reg.cfg.revenue_m,
                   "r_alloc": list(reg.cfg.revenue_r_alloc)},
        "memory_bytes": reg.revenue.memory_bytes(),
        "n_clipped": reg.revenue.n_clipped(),
    }
