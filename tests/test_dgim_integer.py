"""Kiểm định DGIM mở rộng cho tổng số nguyên (slide tr.66)."""

from __future__ import annotations

import random

import numpy as np
import pytest

from cityflow.sketches.dgim_integer import (
    DGIMInteger, compute_bit_counts, high_bit_allocation, predicted_error_weight,
    sqrt_weighted_allocation, uniform_allocation,
)


# ---------------------------------------------------------------------------
# Tính đúng đắn cơ bản
# ---------------------------------------------------------------------------


def test_slide_p66_formula():
    """Ước lượng phải đúng công thức sum_i c_i * 2^i của slide tr.66."""
    d = DGIMInteger(N=1_000, m=8, r=2)
    for v in [5, 3, 12, 7]:  # 101, 011, 1100, 0111
        d.update(v)
    per_bit = d.query_per_bit()
    assert d.query() == sum(c << i for i, c in enumerate(per_bit))


def test_small_stream_is_exact():
    """Khi số giá trị ít hơn sức chứa bucket, tổng phải chính xác tuyệt đối."""
    values = [10, 25, 3, 7, 100]
    d = DGIMInteger(N=1_000, m=8, r=8)
    for v in values:
        d.update(v)
    assert d.query() == sum(values)


def test_clipping_is_counted():
    """Giá trị vượt 2^m - 1 phải bị kẹp trần VÀ được đếm.

    Dùng r=8 chứ không phải r=2: với 4 giá trị, luồng bit đông nhất chỉ có 3 bit 1,
    nên r=8 giữ mọi bucket ở cỡ 1 và quy tắc "trừ nửa bucket cũ nhất" trừ đi 1//2 = 0,
    cho tổng chính xác tuyệt đối. Với r=2, luồng bit có 3 bit 1 đã phải gộp thành
    bucket cỡ 2, và phép trừ nửa bucket làm mất chính xác — đó là hành vi ĐÚNG của
    DGIM, không phải lỗi. Test này chỉ kiểm cơ chế kẹp trần, nên phải tách khỏi
    nhiễu do xấp xỉ.
    """
    d = DGIMInteger(N=100, m=8, r=8)  # trần = 255
    for v in [100, 300, 500, 50]:
        d.update(v)
    assert d.n_clipped() == 2
    assert d.query() == 100 + 255 + 255 + 50


def test_approximation_loses_precision_even_on_tiny_streams():
    """Với r=2, DGIM mất chính xác ngay cả trên luồng rất ngắn.

    Không phải lỗi: quy tắc slide tr.64 luôn trừ nửa kích thước bucket cũ nhất.
    Hễ bucket cũ nhất có cỡ >= 2 thì ước lượng lệch. Ghi lại làm tài liệu hành vi.
    """
    d = DGIMInteger(N=100, m=8, r=2)
    for v in [100, 255, 255, 50]:
        d.update(v)
    exact = 100 + 255 + 255 + 50
    assert d.query() < exact
    assert abs(d.query() - exact) / exact < 0.5


def test_negative_clamped_to_zero():
    """Doanh thu âm (167 bản ghi trong dữ liệu thật) được kẹp về 0."""
    d = DGIMInteger(N=100, m=8, r=4)
    for v in [-30, 20, -5, 10]:
        d.update(v)
    assert d.query() == 30


def test_zero_values_dont_touch_any_stream():
    """Giá trị 0 không có bit 1 nào -> không luồng bit nào bị chạm."""
    d = DGIMInteger(N=100, m=8, r=2)
    for _ in range(50):
        d.update(0)
    assert d.query() == 0
    assert all(s.n_buckets() == 0 for s in d.streams)


def test_error_bound_on_random_stream():
    """Sai số tương đối của tổng phải nhỏ trên luồng ngẫu nhiên."""
    rng = random.Random(5)
    N = 2_000
    values = [rng.randint(0, 200) for _ in range(20_000)]

    d = DGIMInteger(N=N, m=8, r=8)
    for v in values:
        d.update(v)

    exact = sum(values[-N:])
    rel_err = abs(d.query() - exact) / exact
    assert rel_err <= 0.5, f"sai số {rel_err:.3f} vượt ngưỡng"


def test_error_decreases_with_budget():
    """Tăng ngân sách r phải giảm sai số."""
    rng = random.Random(9)
    N = 2_000
    values = [rng.randint(0, 200) for _ in range(20_000)]
    exact = sum(values[-N:])

    errs = {}
    for r in (2, 8, 32):
        d = DGIMInteger(N=N, m=8, r=r)
        for v in values:
            d.update(v)
        errs[r] = abs(d.query() - exact) / exact

    assert errs[32] < errs[2], f"sai số không giảm theo ngân sách: {errs}"


# ---------------------------------------------------------------------------
# Chiến lược phân bổ ngân sách (thực nghiệm E4 / giả thuyết H1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("budget", [16, 32, 64, 128])
def test_allocations_respect_budget(budget):
    """Ba chiến lược phải dùng ĐÚNG cùng một ngân sách — điều kiện để so sánh công bằng."""
    m = 8
    counts = np.array([10_000_000, 9_000_000, 9_000_000, 11_000_000,
                       8_000_000, 3_800_000, 1_000_000, 180_000])
    for alloc in (uniform_allocation(m, budget),
                  high_bit_allocation(m, budget),
                  sqrt_weighted_allocation(m, budget, counts)):
        assert len(alloc) == m
        assert sum(alloc) == budget, f"ngân sách lệch: {alloc} = {sum(alloc)} != {budget}"
        assert all(r >= 2 for r in alloc), f"có r < 2 (cấu hình suy biến): {alloc}"


def test_sqrt_allocation_peaks_at_middle_bits():
    """Với phân phối doanh thu thật, r_i lớn nhất phải rơi vào các bit GIỮA.

    Đây là điểm bác bỏ dạng ngây thơ của H1: trọng số 2^i tăng theo i nhưng tần
    suất c_i giảm theo i, nên tích 2^i·c_i đạt cực đại ở giữa dải chứ không ở bit
    cao nhất. Số liệu thật (FHVHV 2024-01) cho cực đại tại bit 4.
    """
    m = 8
    # c_i đo trên dữ liệu thật, xem docs/e4_h1_results.json
    counts = np.array([10_008_230, 9_253_660, 9_233_252, 11_876_860,
                       8_693_146, 3_846_413, 1_040_210, 178_927])
    alloc = sqrt_weighted_allocation(m, 64, counts)
    peak = int(np.argmax(alloc))
    assert 2 <= peak <= 5, f"đỉnh phân bổ ở bit {peak}, kỳ vọng nằm giữa dải: {alloc}"
    assert alloc[peak] > alloc[m - 1], "bit cao nhất không được nhận nhiều r nhất"


def test_budget_16_forces_uniform():
    """Ngân sách 16 với m=8 là mức tối thiểu: mọi chiến lược buộc phải cho r_i = 2.

    Giải thích vì sao E4 không thấy khác biệt nào ở ngân sách 16 — không phải vì
    H1 sai mà vì không còn bậc tự do nào để phân bổ.
    """
    m, budget = 8, 16
    counts = np.array([10_008_230, 9_253_660, 9_233_252, 11_876_860,
                       8_693_146, 3_846_413, 1_040_210, 178_927])
    for alloc in (uniform_allocation(m, budget),
                  high_bit_allocation(m, budget),
                  sqrt_weighted_allocation(m, budget, counts)):
        assert alloc == [2] * m


def test_predicted_error_ranks_sqrt_best():
    """Mô hình lý thuyết E ~ sum 2^i·c_i/(2r_i) phải xếp sqrt_weighted tốt nhất.

    Đây là dự đoán của lý thuyết TRƯỚC khi đo. Thực nghiệm E4 xác nhận nó đúng.
    """
    m, budget = 8, 32
    counts = np.array([10_008_230, 9_253_660, 9_233_252, 11_876_860,
                       8_693_146, 3_846_413, 1_040_210, 178_927])

    e_uniform = predicted_error_weight(uniform_allocation(m, budget), counts, m)
    e_high = predicted_error_weight(high_bit_allocation(m, budget), counts, m)
    e_sqrt = predicted_error_weight(sqrt_weighted_allocation(m, budget, counts), counts, m)

    assert e_sqrt < e_uniform, f"sqrt không tốt hơn uniform: {e_sqrt} vs {e_uniform}"
    assert e_sqrt < e_high, f"sqrt không tốt hơn high_bit: {e_sqrt} vs {e_high}"


def test_compute_bit_counts():
    values = np.array([0b0001, 0b0011, 0b0111, 0b1111], dtype=np.int64)
    counts = compute_bit_counts(values, 4)
    assert counts.tolist() == [4, 3, 2, 1]


def test_r_alloc_length_validated():
    with pytest.raises(ValueError, match="phải có đúng 8 phần tử"):
        DGIMInteger(N=100, m=8, r_alloc=[2, 2, 2])


def test_memory_scales_with_m():
    """Bộ nhớ tổng phải xấp xỉ m lần bộ nhớ một luồng DGIM."""
    rng = random.Random(11)
    d = DGIMInteger(N=10_000, m=8, r=2)
    for _ in range(50_000):
        d.update(rng.randint(0, 255))
    per_stream = [s.memory_bytes() for s in d.streams]
    assert d.memory_bytes() == sum(per_stream)
    assert len(per_stream) == 8
