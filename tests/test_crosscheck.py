"""Thực nghiệm E12 — kiểm định chéo cài đặt from scratch với thư viện.

Đây là điều kiện của quyết định "viết from scratch phần lõi, đối chiếu với thư
viện để chứng minh đúng đắn". Sai lệch cho phép: BẰNG KHÔNG.

Thư viện đối chứng: mlxtend.frequent_patterns.fpgrowth và apriori.
"""

from __future__ import annotations

import random

import pandas as pd
import pytest
from mlxtend.frequent_patterns import apriori as mlx_apriori
from mlxtend.frequent_patterns import fpgrowth as mlx_fpgrowth

from cityflow.mining.apriori import apriori
from cityflow.mining.fpgrowth import fpgrowth

SLIDE_DB = [
    list("facdgimp"),
    list("abcflmo"),
    list("bfhjo"),
    list("bcksp"),
    list("afcelpmn"),
]


def _to_onehot(db: list[list]) -> pd.DataFrame:
    """mlxtend yêu cầu ma trận boolean giao dịch × item."""
    items = sorted({it for txn in db for it in txn}, key=str)
    return pd.DataFrame([[it in set(txn) for it in items] for txn in db], columns=items)


def _mlx_result(df: pd.DataFrame, min_sup_ratio: float, n: int,
                use_fp: bool = True) -> dict[frozenset, int]:
    fn = mlx_fpgrowth if use_fp else mlx_apriori
    out = fn(df, min_support=min_sup_ratio, use_colnames=True)
    return {frozenset(row.itemsets): round(row.support * n) for row in out.itertuples()}


@pytest.mark.parametrize("min_support", [1, 2, 3, 4])
def test_fpgrowth_matches_mlxtend_on_slide_db(min_support):
    """Cài đặt của nhóm phải khớp TUYỆT ĐỐI với mlxtend trên ví dụ của slide."""
    n = len(SLIDE_DB)
    ours = fpgrowth(SLIDE_DB, min_support)
    theirs = _mlx_result(_to_onehot(SLIDE_DB), min_support / n, n)
    assert ours == theirs, (
        f"lệch tại min_sup={min_support}\n"
        f"  chỉ có ở bản của nhóm: {set(ours) - set(theirs)}\n"
        f"  chỉ có ở mlxtend:      {set(theirs) - set(ours)}"
    )


@pytest.mark.parametrize("seed", range(10))
def test_fpgrowth_matches_mlxtend_on_random_db(seed):
    """Kiểm chứng chéo trên CSDL ngẫu nhiên, nhiều mức min_support."""
    rng = random.Random(seed)
    db = [rng.sample(range(14), rng.randint(2, 8)) for _ in range(150)]
    df = _to_onehot(db)
    n = len(db)
    for min_support in (5, 15, 40):
        ours = fpgrowth(db, min_support)
        theirs = _mlx_result(df, min_support / n, n)
        assert ours == theirs, f"lệch tại seed={seed}, min_sup={min_support}"


@pytest.mark.parametrize("seed", range(5))
def test_apriori_matches_mlxtend(seed):
    """Cài đặt Apriori đối chứng cũng phải khớp thư viện."""
    rng = random.Random(100 + seed)
    db = [rng.sample(range(12), rng.randint(2, 6)) for _ in range(120)]
    df = _to_onehot(db)
    n = len(db)
    for min_support in (6, 20):
        ours, _ = apriori(db, min_support)
        theirs = _mlx_result(df, min_support / n, n, use_fp=False)
        assert ours == theirs, f"lệch tại seed={seed}, min_sup={min_support}"


def test_all_three_implementations_agree():
    """FP-Growth của nhóm == Apriori của nhóm == mlxtend.

    Ba đường đi độc lập cho cùng một kết quả là bằng chứng mạnh về tính đúng đắn.
    """
    rng = random.Random(999)
    db = [rng.sample(range(10), rng.randint(2, 6)) for _ in range(200)]
    n = len(db)
    min_support = 20

    ours_fp = fpgrowth(db, min_support)
    ours_ap, _ = apriori(db, min_support)
    theirs = _mlx_result(_to_onehot(db), min_support / n, n)

    assert ours_fp == ours_ap == theirs
    assert len(ours_fp) > 0, "phép kiểm chứng vô nghĩa nếu không tìm được mẫu nào"
