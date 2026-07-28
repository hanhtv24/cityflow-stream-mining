"""Apriori — cài đặt ĐỐI CHỨNG để đo ba điểm nghẽn mà slide tr.19 nêu.

Cài đặt from scratch theo slide chương Frequent Patterns tr.16-19
(Agrawal & Srikant, VLDB'94).

Nguyên lý tỉa Apriori (tr.16):
    "Nếu có bất kỳ tập mục nào không thường xuyên, tập cha của nó không nên
     được sinh ra / kiểm tra."

Ba điểm nghẽn tính toán (tr.19) — chính là thứ cần ĐO để so với FP-Growth:
    1. Quét CSDL giao dịch nhiều lần
    2. Số lượng ứng viên khổng lồ
    3. Chi phí đếm hỗ trợ cho các ứng viên
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations


@dataclass
class AprioriStats:
    """Số liệu để minh chứng ba điểm nghẽn của slide tr.19."""

    db_scans: int = 0
    candidates_generated: int = 0
    candidates_by_level: list[int] = field(default_factory=list)
    frequent_by_level: list[int] = field(default_factory=list)
    support_checks: int = 0
    """Số phép kiểm tra "ứng viên có nằm trong giao dịch này không" — điểm nghẽn 3."""


def apriori(transactions, min_support: int) -> tuple[dict[frozenset, int], AprioriStats]:
    """Khai phá tập mục thường xuyên bằng Apriori, kèm số liệu điểm nghẽn."""
    transactions = [frozenset(t) for t in transactions]
    stats = AprioriStats()
    result: dict[frozenset, int] = {}

    # --- L1: tập mục 1 phần tử thường xuyên ---
    counts: dict = {}
    stats.db_scans += 1
    for txn in transactions:
        for item in txn:
            counts[item] = counts.get(item, 0) + 1

    stats.candidates_generated += len(counts)
    stats.candidates_by_level.append(len(counts))

    current = {frozenset([it]): c for it, c in counts.items() if c >= min_support}
    result.update(current)
    stats.frequent_by_level.append(len(current))

    k = 2
    while current:
        candidates = _generate_candidates(list(current), k)
        stats.candidates_generated += len(candidates)
        stats.candidates_by_level.append(len(candidates))
        if not candidates:
            stats.frequent_by_level.append(0)
            break

        # Điểm nghẽn 1 + 3: quét lại CSDL và đếm hỗ trợ cho mọi ứng viên.
        stats.db_scans += 1
        cand_counts = dict.fromkeys(candidates, 0)
        for txn in transactions:
            for cand in candidates:
                stats.support_checks += 1
                if cand <= txn:
                    cand_counts[cand] += 1

        current = {c: n for c, n in cand_counts.items() if n >= min_support}
        result.update(current)
        stats.frequent_by_level.append(len(current))
        k += 1

    return result, stats


def _generate_candidates(frequent_k: list[frozenset], k: int) -> list[frozenset]:
    """Sinh ứng viên cỡ k từ tập thường xuyên cỡ k-1, có áp dụng tỉa Apriori.

    Tỉa (slide tr.16): loại ngay ứng viên có bất kỳ tập con cỡ k-1 nào KHÔNG
    thường xuyên — theo tính chất đóng xuống (downward closure, tr.15).
    """
    freq_set = set(frequent_k)
    candidates = []
    n = len(frequent_k)
    for i in range(n):
        for j in range(i + 1, n):
            union = frequent_k[i] | frequent_k[j]
            if len(union) != k:
                continue
            # Tỉa: mọi tập con cỡ k-1 phải thường xuyên.
            if all(frozenset(sub) in freq_set for sub in combinations(sorted(union), k - 1)):
                candidates.append(union)
    return list(set(candidates))
