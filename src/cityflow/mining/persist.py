"""Ghi kết quả khai phá mẫu (FP-Growth + luật) vào PostgreSQL.

Tách khỏi fpgrowth.py/rules.py để tầng mining không phụ thuộc SQLAlchemy —
các script/test không cần CSDL vẫn import và chạy được (đúng cách các test hiện
tại trong tests/test_mining.py và tests/test_crosscheck.py không cần DB).
"""

from __future__ import annotations

import uuid

from sqlalchemy import insert
from sqlalchemy.engine import Engine

from .fpgrowth import closed_itemsets, maximal_itemsets
from .rules import Rule


def save_mining_run(
    engine: Engine,
    *,
    month: str,
    percentile: float,
    min_support: int,
    n_baskets: int,
    frequent: dict[frozenset, int],
    rules: list[Rule],
    elapsed_ms: float | None = None,
) -> uuid.UUID:
    """Lưu một lần chạy khai phá đầy đủ: metadata + tập mục + luật."""
    from ..db.models import association_rules, frequent_itemsets, mining_runs

    run_id = uuid.uuid4()
    closed = set(closed_itemsets(frequent))
    maximal = set(maximal_itemsets(frequent))

    with engine.begin() as conn:
        conn.execute(insert(mining_runs).values(
            run_id=run_id, month=month, percentile=percentile,
            min_support=min_support, n_baskets=n_baskets,
            algorithm="fpgrowth", elapsed_ms=elapsed_ms,
        ))

        if frequent:
            conn.execute(insert(frequent_itemsets), [
                {
                    "run_id": run_id,
                    "items": sorted(itemset),
                    "support_count": count,
                    "support_rel": count / n_baskets,
                    "is_closed": itemset in closed,
                    "is_maximal": itemset in maximal,
                }
                for itemset, count in frequent.items()
            ])

        if rules:
            conn.execute(insert(association_rules), [
                {
                    "run_id": run_id,
                    "antecedent": sorted(r.antecedent),
                    "consequent": sorted(r.consequent),
                    "sup_a": r.stats.sup_a, "sup_b": r.stats.sup_b,
                    "sup_ab": r.stats.sup_ab, "n_transactions": r.stats.n,
                    **{k: v for k, v in r.measures.items()},
                }
                for r in rules
            ])

    return run_id
