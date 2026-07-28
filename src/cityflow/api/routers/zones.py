from __future__ import annotations

from fastapi import APIRouter

from ..state import state

router = APIRouter()


@router.get("/zones")
def list_zones() -> list[dict]:
    """Danh mục 265 khu vực — dùng để dựng bản đồ nhiệt và bộ lọc trên dashboard."""
    from ...config import AIRPORT_ZONES

    return [
        {
            "location_id": zid,
            "zone_name": name,
            "borough": state.zone_boroughs.get(zid, "?"),
            "is_airport": zid in AIRPORT_ZONES,
        }
        for zid, name in sorted(state.zone_names.items())
    ]
