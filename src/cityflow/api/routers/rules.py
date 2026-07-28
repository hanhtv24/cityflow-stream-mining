"""Q6 — luật kết hợp, xếp hạng theo 10 độ đo interestingness.

Tầng bắt buộc — trả lời câu hỏi "đâu là phần khai phá dữ liệu?" (Phase 4 §5,
docs/07_KET_QUA_E5_E6.md §10).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...mining.interestingness import ALL_MEASURES
from ...mining.rules import rank_by, rank_correlation
from ..state import state

router = APIRouter()


def _serialize(rule) -> dict:
    return {
        "antecedent": sorted(rule.antecedent),
        "antecedent_names": [state.zone_names.get(z, "?") for z in sorted(rule.antecedent)],
        "consequent": sorted(rule.consequent),
        "consequent_names": [state.zone_names.get(z, "?") for z in sorted(rule.consequent)],
        "measures": {k: round(v, 4) for k, v in rule.measures.items()},
        "stats": {"n": rule.stats.n, "sup_a": rule.stats.sup_a,
                  "sup_b": rule.stats.sup_b, "sup_ab": rule.stats.sup_ab},
    }


@router.get("/rules")
def get_rules(
    measure: str = Query("kulczynski", description=f"Một trong: {', '.join(ALL_MEASURES)}"),
    top_k: int = Query(20, ge=1, le=200),
) -> dict:
    """Luật đồng ùn tắc, xếp theo độ đo tùy chọn.

    Đổi `measure` từ lift sang kulczynski có thể ĐẢO LỘN thứ hạng — xem
    docs/09_KET_QUA_MINING.md §E10 để biết mức độ đảo lộn đo được trên dữ liệu thật.
    """
    if measure not in ALL_MEASURES:
        raise HTTPException(400, f"Độ đo không hợp lệ. Chọn: {list(ALL_MEASURES)}")
    if not state.mining.ready:
        return {"ready": False, "rules": []}

    top = rank_by(state.mining.rules, measure, top_k)
    return {
        "ready": True, "measure": measure, "n_total_rules": len(state.mining.rules),
        "n_baskets": state.mining.n_baskets, "min_support": state.mining.min_support,
        "percentile": state.mining.percentile,
        "rules": [_serialize(r) for r in top],
    }


@router.get("/rules/compare")
def compare_measures() -> dict:
    """Tương quan hạng Spearman giữa các cặp độ đo — cho thấy mức đảo lộn thứ hạng."""
    if not state.mining.ready:
        return {"ready": False}

    rules = state.mining.rules
    pairs = [("lift", "kulczynski"), ("confidence", "kulczynski"),
             ("support", "kulczynski"), ("chi_square", "cosine")]
    return {
        "ready": True,
        "correlations": [
            {"measure_a": a, "measure_b": b, "spearman_rho": round(rank_correlation(rules, a, b), 4)}
            for a, b in pairs
        ],
    }
