"""Kiểm định tầng khai phá mẫu: FP-Growth, Apriori, mẫu đóng/cực đại, 10 độ đo.

Nguyên tắc: mỗi ví dụ số trong slide trở thành một unit test.
"""

from __future__ import annotations

import pytest

from cityflow.mining.apriori import apriori
from cityflow.mining.fpgrowth import (
    closed_itemsets, fpgrowth, maximal_itemsets, reconstruct_from_closed,
)
from cityflow.mining.fptree import FPTree
from cityflow.mining.interestingness import (
    ALL_MEASURES, NOT_NULL_INVARIANT, NULL_INVARIANT, RuleStats,
    add_null_transactions, compute_all, confidence, cosine, kulczynski, lift, support,
)


# ===========================================================================
# Ví dụ chuẩn của slide tr.21-22
# ===========================================================================

SLIDE_DB = [
    list("facdgimp"),
    list("abcflmo"),
    list("bfhjo"),
    list("bcksp"),
    list("afcelpmn"),
]
"""Slide tr.21: 5 giao dịch, min_support = 3."""


def test_slide_p22_f_list():
    """Slide tr.22: min_sup=3 -> f, c, a, b, m, p đều có tần suất 4,4,3,3,3,3."""
    tree = FPTree(SLIDE_DB, min_support=3)
    counts = {it: tree.header[it][0] for it in tree.f_list}
    assert counts == {"f": 4, "c": 4, "a": 3, "b": 3, "m": 3, "p": 3}
    # f-list sắp giảm dần tần suất; hòa thì theo thứ tự item cho tất định.
    assert tree.f_list == ["c", "f", "a", "b", "m", "p"]


def test_slide_p21_ordered_transactions():
    """Slide tr.21 liệt kê giao dịch đã lọc và sắp lại theo f-list.

    Slide dùng f-list (f, c, a, b, m, p) vì nó phá thế hòa f=c=4 theo thứ tự xuất
    hiện. Cài đặt này phá hòa theo thứ tự item (c trước f) để kết quả TẤT ĐỊNH —
    hai lần chạy luôn cho cùng một cây. Tập mục thường xuyên tìm được không đổi,
    chỉ hình dạng cây khác.
    """
    tree = FPTree(SLIDE_DB, min_support=3)
    rank = {it: i for i, it in enumerate(tree.f_list)}
    ordered = []
    for txn in SLIDE_DB:
        f = [it for it in txn if it in rank]
        f.sort(key=lambda it: rank[it])
        ordered.append("".join(f))
    assert ordered == ["cfamp", "cfabm", "fb", "cbp", "cfamp"]


def test_fpgrowth_finds_expected_patterns_on_slide_db():
    """Các mẫu mà slide nêu đích danh phải xuất hiện với đúng số đếm."""
    freq = fpgrowth(SLIDE_DB, min_support=3)
    assert freq[frozenset("f")] == 4
    assert freq[frozenset("c")] == 4
    assert freq[frozenset("cf")] == 3
    assert freq[frozenset("cfam")] == 3
    assert freq[frozenset("cp")] == 3


# ===========================================================================
# Kiểm chứng chéo FP-Growth <-> Apriori
# ===========================================================================


@pytest.mark.parametrize("min_support", [1, 2, 3, 4])
def test_fpgrowth_matches_apriori_on_slide_db(min_support):
    """Hai thuật toán độc lập phải cho KẾT QUẢ Y HỆT — cả tập mục lẫn số đếm."""
    fp = fpgrowth(SLIDE_DB, min_support)
    ap, _ = apriori(SLIDE_DB, min_support)
    assert fp == ap, f"lệch tại min_sup={min_support}"


@pytest.mark.parametrize("seed", range(8))
def test_fpgrowth_matches_apriori_on_random_db(seed):
    """Kiểm chứng chéo trên CSDL ngẫu nhiên — bắt các trường hợp biên."""
    import random
    rng = random.Random(seed)
    db = [rng.sample(range(12), rng.randint(1, 7)) for _ in range(120)]
    for min_sup in (3, 6, 12):
        assert fpgrowth(db, min_sup) == apriori(db, min_sup)[0], \
            f"lệch tại seed={seed}, min_sup={min_sup}"


def test_empty_and_degenerate_inputs():
    assert fpgrowth([], 1) == {}
    assert fpgrowth([[], [], []], 1) == {}
    # min_support lớn hơn số giao dịch -> không có mẫu nào
    assert fpgrowth(SLIDE_DB, 99) == {}


def test_single_path_optimisation_produces_all_combinations():
    """Slide tr.31-32: cây một đường -> mọi tổ hợp con đều là mẫu thường xuyên."""
    db = [list("abc")] * 5
    freq = fpgrowth(db, min_support=3)
    # 2^3 - 1 = 7 tập con khác rỗng
    assert len(freq) == 7
    assert all(c == 5 for c in freq.values())


# ===========================================================================
# Ba điểm nghẽn của Apriori (slide tr.19)
# ===========================================================================


def test_apriori_stats_expose_bottlenecks():
    """Số liệu phải minh chứng được ba điểm nghẽn slide tr.19 nêu."""
    _, stats = apriori(SLIDE_DB, min_support=2)
    assert stats.db_scans > 1, "điểm nghẽn 1: phải quét CSDL nhiều lần"
    assert stats.candidates_generated > 0, "điểm nghẽn 2: phải sinh ứng viên"
    assert stats.support_checks > 0, "điểm nghẽn 3: phải đếm hỗ trợ"
    assert len(stats.candidates_by_level) >= 2


def test_apriori_generates_more_candidates_than_frequent():
    """Bản chất điểm nghẽn 2: số ứng viên vượt xa số mẫu thực sự thường xuyên."""
    _, stats = apriori(SLIDE_DB, min_support=3)
    assert stats.candidates_generated > sum(stats.frequent_by_level)


# ===========================================================================
# Mẫu đóng và mẫu cực đại (slide tr.13-14)
# ===========================================================================


def test_slide_p14_closed_and_maximal():
    """Slide tr.14: DB = {<a1..a100>, <a1..a50>}, min_sup = 1.

    Tập ĐÓNG: <a1..a100> (xuất hiện 1 lần) và <a1..a50> (xuất hiện 2 lần) — cả hai
    có số đếm riêng biệt và không có tập cha cùng số đếm.
    Tập CỰC ĐẠI: chỉ <a1..a100> — nó thường xuyên và không có tập cha thường xuyên.

    Dùng quy mô nhỏ (a1..a6 và a1..a3) vì 2^100 tập con là bất khả thi; tính chất
    cần kiểm chứng không đổi.
    """
    db = [list(range(6)), list(range(3))]
    freq = fpgrowth(db, min_support=1)
    closed = closed_itemsets(freq)
    maximal = maximal_itemsets(freq)

    assert frozenset(range(6)) in closed
    assert frozenset(range(3)) in closed
    assert closed[frozenset(range(6))] == 1
    assert closed[frozenset(range(3))] == 2

    assert list(maximal) == [frozenset(range(6))]


def test_closed_compression_is_lossless():
    """Slide tr.13: mẫu đóng cho "nén KHÔNG MẤT MÁT".

    Kiểm chứng bằng thực nghiệm thay vì tin lời: khôi phục toàn bộ tập thường xuyên
    kèm số đếm từ tập đóng, rồi so với kết quả gốc.
    """
    import random
    rng = random.Random(42)
    db = [rng.sample(range(10), rng.randint(2, 6)) for _ in range(200)]
    freq = fpgrowth(db, min_support=10)
    closed = closed_itemsets(freq)

    recovered = reconstruct_from_closed(closed)
    recovered = {k: v for k, v in recovered.items() if v >= 10}

    assert recovered == freq, "nén bằng mẫu đóng bị MẤT MÁT"


def test_maximal_is_subset_of_closed():
    """Mọi mẫu cực đại đều là mẫu đóng, nhưng không ngược lại."""
    import random
    rng = random.Random(7)
    db = [rng.sample(range(10), rng.randint(2, 6)) for _ in range(200)]
    freq = fpgrowth(db, min_support=10)
    closed, maximal = closed_itemsets(freq), maximal_itemsets(freq)
    assert set(maximal) <= set(closed)
    assert len(maximal) <= len(closed) <= len(freq)


# ===========================================================================
# Độ đo interestingness (slide tr.36-39)
# ===========================================================================


def _basketball_cereal() -> RuleStats:
    """Bảng chéo slide tr.36:
                    Bóng rổ   Không BR   Tổng
        Ngũ cốc       2000      1750      3750
        Không NC      1000       250      1250
        Tổng          3000      2000      5000
    """
    return RuleStats(n=5000, sup_a=3000, sup_b=3750, sup_ab=2000)


def test_slide_p36_basketball_cereal_confidence_is_misleading():
    """Slide tr.36: luật "chơi bóng rổ -> ăn ngũ cốc" [40%, 66,7%] gây HIỂU LẦM.

    Vì tỷ lệ ăn ngũ cốc chung là 75% > 66,7% — chơi bóng rổ thực ra làm GIẢM khả
    năng ăn ngũ cốc, dù độ tin cậy nghe có vẻ cao.
    """
    s = _basketball_cereal()
    assert support(s) == pytest.approx(0.40)
    assert confidence(s) == pytest.approx(2000 / 3000, abs=1e-4)  # 66,7%
    assert s.p_b() == pytest.approx(0.75)  # tỷ lệ chung CAO HƠN độ tin cậy
    assert confidence(s) < s.p_b()


def test_slide_p36_lift_values():
    """Slide tr.36: lift(BR, NC) = 0,89 và lift(BR, không NC) = 1,33."""
    s = _basketball_cereal()
    assert lift(s) == pytest.approx(0.89, abs=0.005)

    not_cereal = RuleStats(n=5000, sup_a=3000, sup_b=1250, sup_ab=1000)
    assert lift(not_cereal) == pytest.approx(1.33, abs=0.005)


# --- Tính bất biến với giao dịch rỗng — trọng tâm của slide tr.39 -----------


@pytest.mark.parametrize("name", NULL_INVARIANT)
@pytest.mark.parametrize("k", [1_000, 100_000, 10_000_000])
def test_null_invariant_measures_are_unchanged(name, k):
    """Năm độ đo bất biến phải cho giá trị Y HỆT khi thêm giao dịch rỗng.

    Thêm tới 10 triệu giao dịch rỗng — gấp 2000 lần CSDL gốc — mà giá trị không đổi
    một chữ số thập phân nào.
    """
    s = _basketball_cereal()
    fn = ALL_MEASURES[name]
    assert fn(add_null_transactions(s, k)) == pytest.approx(fn(s), abs=1e-12)


@pytest.mark.parametrize("name", ["lift", "chi_square", "support"])
def test_non_null_invariant_measures_drift(name):
    """Lift, chi-bình phương và support TRÔI khi thêm giao dịch rỗng — slide tr.39."""
    s = _basketball_cereal()
    fn = ALL_MEASURES[name]
    before = fn(s)
    after = fn(add_null_transactions(s, 100_000))
    assert abs(after - before) > 1e-6, f"{name} đáng lẽ phải trôi"


def test_confidence_is_null_invariant_but_asymmetric():
    """Độ tin cậy KHÔNG đổi theo giao dịch rỗng, nhưng KHÔNG đối xứng.

    Slide tr.38 xếp confidence có P1=No, O1=No — nó bỏ qua hoàn toàn sup_b, nên
    không phát hiện được trường hợp B vốn đã phổ biến sẵn (phản ví dụ "mua óc chó
    -> mua sữa [1%, 80%]" ở tr.37 khi 85% khách vốn đã mua sữa).
    """
    s = _basketball_cereal()
    assert confidence(add_null_transactions(s, 50_000)) == pytest.approx(confidence(s))

    reverse = RuleStats(n=s.n, sup_a=s.sup_b, sup_b=s.sup_a, sup_ab=s.sup_ab)
    assert confidence(reverse) != pytest.approx(confidence(s))


def test_kulczynski_and_cosine_are_symmetric():
    """Kulczynski và Cosine đối xứng khi hoán vị A và B (tính chất O1, slide tr.38)."""
    s = _basketball_cereal()
    reverse = RuleStats(n=s.n, sup_a=s.sup_b, sup_b=s.sup_a, sup_ab=s.sup_ab)
    assert kulczynski(reverse) == pytest.approx(kulczynski(s))
    assert cosine(reverse) == pytest.approx(cosine(s))


def test_null_transaction_count_is_correct():
    s = _basketball_cereal()
    assert s.n_null == 250  # ô ~BR & ~NC trong bảng chéo


def test_compute_all_returns_ten_measures():
    assert len(compute_all(_basketball_cereal())) == 10
    assert len(NULL_INVARIANT) + len(NOT_NULL_INVARIANT) == 10


def test_measures_handle_zero_support():
    """Không được chia cho 0 khi tập mục có hỗ trợ bằng 0."""
    s = RuleStats(n=100, sup_a=0, sup_b=0, sup_ab=0)
    for name, value in compute_all(s).items():
        assert value == 0.0 or not (value != value), f"{name} trả về giá trị lỗi"
