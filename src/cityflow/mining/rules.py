"""Sinh luật kết hợp và xếp hạng bằng 10 độ đo.

Slide tr.12: tìm mọi luật X -> Y thỏa min_support và min_confidence.

Nhưng độ tin cậy một mình gây hiểu lầm (slide tr.36-37), nên mọi luật ở đây đều
được tính đủ 10 độ đo và có thể xếp hạng theo bất kỳ độ đo nào.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

from .interestingness import RuleStats, compute_all


@dataclass(slots=True)
class Rule:
    antecedent: frozenset
    consequent: frozenset
    stats: RuleStats
    measures: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.measures:
            self.measures = compute_all(self.stats)

    def __repr__(self) -> str:
        a = ",".join(map(str, sorted(self.antecedent)))
        c = ",".join(map(str, sorted(self.consequent)))
        return (f"{{{a}}} -> {{{c}}} "
                f"(sup={self.measures['support']:.3f}, "
                f"conf={self.measures['confidence']:.3f}, "
                f"kulc={self.measures['kulczynski']:.3f})")


def generate_rules(
    frequent: dict[frozenset, int],
    n_transactions: int,
    min_confidence: float = 0.5,
    max_antecedent_size: int | None = None,
) -> list[Rule]:
    """Sinh mọi luật X -> Y từ tập mục thường xuyên.

    Với mỗi tập mục thường xuyên cỡ >= 2, thử mọi cách tách thành tiền đề và hệ quả.
    """
    rules: list[Rule] = []

    for itemset, sup_ab in frequent.items():
        if len(itemset) < 2:
            continue
        items = sorted(itemset, key=str)
        for size in range(1, len(items)):
            if max_antecedent_size is not None and size > max_antecedent_size:
                break
            for ante in combinations(items, size):
                antecedent = frozenset(ante)
                consequent = itemset - antecedent
                sup_a = frequent.get(antecedent)
                sup_b = frequent.get(consequent)
                if sup_a is None or sup_b is None:
                    # Có thể xảy ra khi tập cha thường xuyên nhưng ta chưa lưu tập
                    # con — không xảy ra với FP-Growth đầy đủ, nhưng phòng thủ.
                    continue
                conf = sup_ab / sup_a
                if conf < min_confidence:
                    continue
                rules.append(Rule(antecedent, consequent,
                                  RuleStats(n_transactions, sup_a, sup_b, sup_ab)))
    return rules


def rank_by(rules: list[Rule], measure: str, top_k: int | None = None) -> list[Rule]:
    """Xếp hạng luật theo một độ đo. Đổi độ đo có thể đảo lộn thứ hạng — đó chính
    là điều thực nghiệm E10 đo."""
    ordered = sorted(rules, key=lambda r: r.measures[measure], reverse=True)
    return ordered[:top_k] if top_k else ordered


def rank_positions(rules: list[Rule], measure: str) -> dict[tuple, int]:
    """Vị trí xếp hạng của từng luật theo một độ đo (1 = cao nhất)."""
    ordered = rank_by(rules, measure)
    return {(r.antecedent, r.consequent): i + 1 for i, r in enumerate(ordered)}


def rank_correlation(rules: list[Rule], measure_a: str, measure_b: str) -> float:
    """Hệ số tương quan hạng Spearman giữa hai độ đo.

    Gần 1 nghĩa là hai độ đo xếp hạng gần như giống nhau; thấp nghĩa là chọn độ đo
    nào sẽ cho tập luật hàng đầu khác hẳn nhau.
    """
    if len(rules) < 2:
        return 1.0
    pos_a = rank_positions(rules, measure_a)
    pos_b = rank_positions(rules, measure_b)
    keys = list(pos_a)
    n = len(keys)
    d2 = sum((pos_a[k] - pos_b[k]) ** 2 for k in keys)
    return 1 - (6 * d2) / (n * (n * n - 1))
