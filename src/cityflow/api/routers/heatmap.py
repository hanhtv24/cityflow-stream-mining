"""Bản đồ nhiệt — nguồn dữ liệu cho màn hình Live Monitor."""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..state import state

router = APIRouter()


@router.get("/heatmap")
def heatmap(k: int | None = Query(None)) -> dict:
    """Ước lượng DGIM cho cả 265 khu vực trong một lần gọi."""
    reg = state.registry
    k = k or reg.cfg.N
    counts = reg.heatmap(k)
    return {
        "k": k, "now": reg.now,
        "zones": [
            {"location_id": z, "zone_name": state.zone_names.get(z, "?"), "count": c}
            for z, c in sorted(counts.items())
        ],
    }
