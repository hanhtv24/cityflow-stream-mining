"""Kiểm định Flajolet-Martin, AMS và Reservoir Sampling.

Mỗi ví dụ số trong slide trở thành một unit test.
"""

from __future__ import annotations

import random
import statistics

import pytest

from cityflow.sketches.ams import AMS, exact_moment
from cityflow.sketches.flajolet_martin import FlajoletMartin, _splitmix64
from cityflow.sketches.reservoir import HashBasedSampler, ReservoirSampler


# ===========================================================================
# FLAJOLET-MARTIN
# ===========================================================================


def test_slide_p37_trailing_zeros_example():
    """Slide tr.37: h(s) = 12 = 1100_2 -> 2 số 0 ở cuối -> r(s) = 2."""
    assert FlajoletMartin._trailing_zeros(0b1100) == 2


def test_slide_p38_max_rule():
    """Slide tr.38: r = 1, 1, 2, 3 -> R = max = 3 -> ước lượng 2^3 = 8."""
    values = [0b0001, 0b0010, 0b1100, 0b1000]
    rs = [FlajoletMartin._trailing_zeros(v) for v in values]
    assert rs == [0, 1, 2, 3]
    assert 2 ** max(rs) == 8


def test_trailing_zeros_edge_cases():
    assert FlajoletMartin._trailing_zeros(1) == 0
    assert FlajoletMartin._trailing_zeros(2) == 1
    assert FlajoletMartin._trailing_zeros(8) == 3
    assert FlajoletMartin._trailing_zeros(0) == 64  # quy ước cho giá trị băm 0


def test_splitmix64_low_bits_are_independent_of_input():
    """Bit THẤP của hàm băm phải độc lập với bit thấp đầu vào.

    Đây là điều kiện sống còn của Flajolet-Martin vì r(s) đếm số 0 Ở CUỐI.

    Hàm affine (a*x + b) mod 2^64 với a lẻ KHÔNG thỏa. Lưu ý khuyết điểm ở đây
    KHÔNG phải mất cân bằng — tính trên dãy 0..9999 thì bit 0 vẫn ra đúng 50/50.
    Khuyết điểm là TÍNH TẤT ĐỊNH: bit 0 của kết quả luôn bằng bit 0 của x XOR một
    hằng số. Nghĩa là với mọi hàm băm affine khác nhau (a_j, b_j khác nhau), r(s)
    vẫn tương quan chặt với nhau, nên m ước lượng "độc lập" thực ra không độc lập
    và cơ chế giảm phương sai bằng nhiều hàm băm mất tác dụng.
    """
    M = (1 << 64) - 1
    a, b = 0x9E3779B97F4A7C15, 12345

    # Affine: quan hệ bit0(hash(x)) XOR bit0(x) là HẰNG SỐ với mọi x.
    affine_rel = {((((a * x + b) & M) & 1) ^ (x & 1)) for x in range(2_000)}
    assert len(affine_rel) == 1, "affine đáng lẽ phải có quan hệ tất định ở bit 0"

    # SplitMix64: quan hệ đó KHÔNG tất định.
    mix_rel = {((_splitmix64(x) & 1) ^ (x & 1)) for x in range(2_000)}
    assert len(mix_rel) == 2, "SplitMix64 phải phá vỡ quan hệ tất định ở bit 0"

    # Và vẫn cân bằng.
    ones = sum(_splitmix64(x) & 1 for x in range(10_000))
    assert 0.45 < ones / 10_000 < 0.55


@pytest.mark.parametrize("true_n", [1_000, 10_000, 100_000])
def test_accuracy_on_known_cardinality(true_n):
    """Sai số TRUNG VỊ qua nhiều hạt giống phải hợp lý.

    Cố ý đo trên 15 hạt giống thay vì một: ước lượng 2^R có phương sai theo cấp số
    nhân, nên khẳng định dựa trên MỘT lần chạy là không có cơ sở thống kê. Một lần
    chạy đơn lẻ từng cho sai số 203% ở true_n=10.000 — không phải lỗi cài đặt mà là
    bản chất phương sai cao của ước lượng, chính là điều slide tr.40 cảnh báo và là
    nội dung thực nghiệm E5 phải định lượng.
    """
    errs = []
    for seed in range(15):
        fm = FlajoletMartin(m=64, g=8, seed=seed)
        for i in range(true_n):
            fm.update(i * 2_654_435_761)  # trải đều không gian khóa
        errs.append(abs(fm.estimate_loglog() - true_n) / true_n)
    median_err = statistics.median(errs)
    assert median_err < 0.35, \
        f"sai số trung vị {median_err:.2%} quá lớn (true_n={true_n:,}, errs={errs})"


@pytest.mark.parametrize("true_n", [1_000, 10_000, 100_000])
def test_slide_scheme_has_stable_multiplicative_bias(true_n):
    """Sơ đồ của slide (trung vị các trung bình 2^R) chệch LÊN khoảng 2,3 lần.

    Đây là phát hiện chính của E5. Điểm quan trọng: bội số chệch ỔN ĐỊNH qua nhiều
    bậc độ lớn, nên nó KHÔNG phải nhiễu ngẫu nhiên mà là đặc tính hệ thống, hiệu
    chỉnh được bằng một hằng số — đúng cách HyperLogLog dùng các hằng số alpha_m.
    """
    ratios = []
    for seed in range(15):
        fm = FlajoletMartin(m=64, g=8, seed=seed)
        for i in range(true_n):
            fm.update(i * 2_654_435_761)
        ratios.append(fm.estimate() / true_n)
    med = statistics.median(ratios)
    assert 1.8 < med < 2.9, f"bội số chệch {med:.2f} nằm ngoài khoảng đã hiệu chuẩn"


def test_literature_phi_makes_things_worse():
    """Hằng số phi = 0,77351 của Flajolet & Martin KHÔNG áp dụng cho sơ đồ này.

    Phi được suy ra cho biến thể "stochastic averaging" (chia bucket theo bit cao),
    không phải cho m hàm băm độc lập cùng lấy max trên toàn luồng. Vì ước lượng vốn
    đã chệch LÊN 2,3 lần, chia thêm cho phi < 1 chỉ làm sai số tăng.
    """
    true_n = 20_000
    err_phi, err_cal = [], []
    for seed in range(10):
        fm = FlajoletMartin(m=64, g=8, seed=seed)
        for i in range(true_n):
            fm.update(i * 2_654_435_761)
        e = fm.all_estimates()
        err_phi.append(abs(e["median_of_means_phi"] - true_n) / true_n)
        err_cal.append(abs(e["median_of_means_cal"] - true_n) / true_n)
    assert statistics.median(err_cal) < statistics.median(err_phi)


def test_loglog_style_has_lower_variance_than_slide_scheme():
    """Trung bình R rồi mũ hóa cho phương sai THẤP HƠN trung bình 2^R.

    Sơ đồ của slide (trung bình các 2^R rồi lấy trung vị) chịu ảnh hưởng nặng của
    ngoại lệ vì 2^R tăng theo cấp số nhân — đúng như tr.40 cảnh báo. Lấy trung bình
    TRƯỚC khi mũ hóa loại bỏ được hiệu ứng này.
    """
    true_n = 20_000
    spread = {}
    for name in ("estimate", "estimate_loglog"):
        ests = []
        for seed in range(15):
            fm = FlajoletMartin(m=64, g=8, seed=seed)
            for i in range(true_n):
                fm.update(i * 2_654_435_761)
            ests.append(getattr(fm, name)())
        spread[name] = statistics.pstdev(ests) / statistics.fmean(ests)
    assert spread["estimate_loglog"] < spread["estimate"], \
        f"phương sai không giảm: {spread}"


def test_duplicates_do_not_change_estimate():
    """Đếm PHÂN BIỆT: nạp lại cùng phần tử không được làm đổi ước lượng."""
    fm = FlajoletMartin(m=32, g=4, seed=2)
    for i in range(5_000):
        fm.update(i)
    before = fm.estimate()
    for _ in range(10):
        for i in range(5_000):
            fm.update(i)
    assert fm.estimate() == before


def test_median_is_always_power_of_two():
    """Slide tr.40: trung vị thuần "luôn là lũy thừa của 2" — hạn chế cố hữu."""
    fm = FlajoletMartin(m=64, g=8, seed=3)
    for i in range(50_000):
        fm.update(i * 7919)
    med = fm.estimate_median()
    assert med == 2 ** round(statistics.log(med, 2)) if med > 0 else True


def test_median_of_means_breaks_power_of_two_constraint():
    """Trung bình trong nhóm phá vỡ ràng buộc lũy thừa 2 — lý do slide khuyến nghị."""
    fm = FlajoletMartin(m=64, g=8, seed=4)
    for i in range(50_000):
        fm.update(i * 7919)
    est = fm.estimate()
    assert est != 2 ** round(statistics.log(est, 2))


def test_more_hash_functions_reduce_variance():
    """Tăng m phải giảm độ phân tán của ước lượng qua nhiều hạt giống."""
    true_n = 20_000
    spread = {}
    for m in (8, 64):
        ests = []
        for seed in range(12):
            fm = FlajoletMartin(m=m, g=min(m, 4), seed=seed)
            for i in range(true_n):
                fm.update(i * 2_654_435_761)
            ests.append(fm.estimate())
        spread[m] = statistics.pstdev(ests) / statistics.fmean(ests)
    assert spread[64] < spread[8], f"phương sai không giảm theo m: {spread}"


def test_invalid_params_rejected():
    with pytest.raises(ValueError):
        FlajoletMartin(m=10, g=3)  # 10 không chia hết cho 3
    with pytest.raises(ValueError):
        FlajoletMartin(m=8, g=16)  # g > m


# ===========================================================================
# AMS
# ===========================================================================


def test_slide_p43_moment_definitions():
    """Slide tr.43: luồng a,b,a,c,a,b -> m_a=3, m_b=2, m_c=1.

    Bậc 0 = 3 (số phần tử phân biệt) · bậc 1 = 6 (độ dài) · bậc 2 = 14 (số bất ngờ)
    """
    stream = ["a", "b", "a", "c", "a", "b"]
    assert exact_moment(stream, 0) == 3
    assert exact_moment(stream, 1) == 6
    assert exact_moment(stream, 2) == 14


def test_slide_p45_surprise_number_examples():
    """Slide tr.45: phân phối đều 5,4,4,4,3 -> 82; có ngoại lệ 16,1,1,1,1 -> 260."""
    even = ["a"] * 5 + ["b"] * 4 + ["c"] * 4 + ["d"] * 4 + ["e"] * 3
    skewed = ["a"] * 16 + ["b", "c", "d", "e"]
    assert exact_moment(even, 2) == 82
    assert exact_moment(skewed, 2) == 260


def test_slide_p48_worked_example():
    """Slide tr.48: luồng 15 phần tử, số bất ngờ thực tế = 59.

    a b c b d a c d a b d c a a b -> m_a=5, m_b=4, m_c=3, m_d=3
    -> 25 + 16 + 9 + 9 = 59

    Slide cũng minh họa ước lượng AMS với 3 biến tại vị trí 3, 8, 13 cho kết quả 55.
    Tái hiện phép tính đó bằng công thức n(2c-1) lấy trung bình.
    """
    stream = list("abcbdacdabdcaab")
    assert len(stream) == 15
    assert exact_moment(stream, 2) == 59

    # Ba biến của slide: X1 tại vị trí 3 (val=c, c=3), X2 tại 8 (val=d, c=2),
    # X3 tại 13 (val=a, c=2).
    n = 15
    counts = [3, 2, 2]
    estimate = (n / 3) * sum(2 * c - 1 for c in counts)
    assert estimate == 55


def test_slide_p50_exercise_stream():
    """Bài tập giảng viên giao ở slide tr.50: luồng 3,1,4,1,3,4,2,1,2.

    m_1 = 3, m_2 = 2, m_3 = 2, m_4 = 2
    Mô-men bậc 2 (số bất ngờ) = 9 + 4 + 4 + 4 = 21
    Mô-men bậc 3              = 27 + 8 + 8 + 8 = 51
    """
    stream = [3, 1, 4, 1, 3, 4, 2, 1, 2]
    assert exact_moment(stream, 2) == 21
    assert exact_moment(stream, 3) == 51


def test_ams_estimator_is_unbiased_on_average():
    """Kỳ vọng của ước lượng AMS phải tiệm cận mô-men thật (chứng minh slide tr.49)."""
    rng = random.Random(5)
    stream = [rng.randint(0, 50) for _ in range(5_000)]
    truth = exact_moment(stream, 2)

    ests = []
    for seed in range(40):
        ams = AMS(k=200, seed=seed)
        for it in stream:
            ams.update(it)
        ests.append(ams.surprise_number())

    mean_est = statistics.fmean(ests)
    assert abs(mean_est - truth) / truth < 0.25, \
        f"ước lượng chệch: TB {mean_est:,.0f} vs thật {truth:,.0f}"


def test_ams_detects_skew():
    """Phân phối lệch phải cho số bất ngờ CAO HƠN hẳn phân phối đều.

    Đây là tính chất mà CityFlow dựa vào để phát hiện ùn tắc (slide tr.45).
    """
    rng = random.Random(7)
    even = [rng.randint(0, 99) for _ in range(10_000)]
    skewed = [0] * 5_000 + [rng.randint(1, 99) for _ in range(5_000)]

    def est(stream):
        a = AMS(k=300, seed=11)
        for it in stream:
            a.update(it)
        return a.surprise_number()

    assert est(skewed) > est(even) * 2


def test_ams_higher_order_moments():
    """Công thức tổng quát n(c^k - (c-1)^k) — slide tr.50."""
    rng = random.Random(13)
    stream = [rng.randint(0, 20) for _ in range(3_000)]
    ams = AMS(k=400, seed=13)
    for it in stream:
        ams.update(it)
    assert ams.estimate_moment(3) > ams.estimate_moment(2) > 0


def test_ams_memory_is_bounded_by_k():
    """Bộ nhớ AMS phải phụ thuộc k, KHÔNG phụ thuộc độ dài luồng."""
    mems = []
    for n in (10_000, 100_000):
        ams = AMS(k=100, seed=17)
        for i in range(n):
            ams.update(i % 500)
        mems.append(ams.memory_bytes())
    assert mems[1] < mems[0] * 1.5, f"bộ nhớ tăng theo độ dài luồng: {mems}"


def test_ams_empty_stream():
    assert AMS(k=10).surprise_number() == 0.0


# ===========================================================================
# RESERVOIR SAMPLING
# ===========================================================================


def test_reservoir_keeps_exactly_s():
    r = ReservoirSampler(s=100, seed=1)
    for i in range(10_000):
        r.update(i)
    assert len(r.sample()) == 100
    assert r.n == 10_000


def test_reservoir_shorter_than_s():
    r = ReservoirSampler(s=100, seed=1)
    for i in range(50):
        r.update(i)
    assert r.sample() == list(range(50))


def test_reservoir_uniform_probability():
    """Bảo đảm cốt lõi: mỗi phần tử có xác suất s/n nằm trong mẫu (slide tr.18-21).

    Chạy nhiều lần và đếm tần suất xuất hiện của từng phần tử — phân phối phải đều.
    """
    n, s, trials = 50, 5, 4_000
    counts = [0] * n
    for seed in range(trials):
        r = ReservoirSampler(s=s, seed=seed)
        for i in range(n):
            r.update(i)
        for x in r.sample():
            counts[x] += 1

    expected = trials * s / n  # = 400
    for i, c in enumerate(counts):
        assert abs(c - expected) / expected < 0.20, \
            f"phần tử {i} xuất hiện {c} lần, kỳ vọng {expected:.0f}"


def test_hash_sampler_rate_is_close_to_target():
    """Lấy mẫu theo khóa phải giữ xấp xỉ a/b số KHÓA phân biệt."""
    s = HashBasedSampler(a=3, b=10)
    for key in range(20_000):
        s.update(key)
    assert 0.28 < s.n_kept / s.n_seen < 0.32


def test_hash_sampler_keeps_all_records_of_a_kept_key():
    """Tính chất then chốt: một khóa đã được giữ thì giữ TOÀN BỘ bản ghi của nó.

    Đây chính là điều phân biệt lấy mẫu theo khóa với lấy mẫu theo bản ghi, và là
    lý do nó tránh được độ chệch mà slide tr.16 chỉ ra.
    """
    s = HashBasedSampler(a=5, b=10)
    kept_keys = {k for k in range(100) if s._keep_key(k)}
    for key in range(100):
        for rep in range(7):
            s.update(key, record=(key, rep))
    for key in kept_keys:
        assert sum(1 for rec in s.kept if rec[0] == key) == 7


def test_hash_sampler_invalid_params():
    with pytest.raises(ValueError):
        HashBasedSampler(a=11, b=10)
    with pytest.raises(ValueError):
        HashBasedSampler(a=0, b=10)


# ===========================================================================
# FLAJOLET-MARTIN — đường đi vector hóa
# ===========================================================================


@pytest.mark.parametrize("m", [8, 64, 256])
def test_update_many_matches_scalar_exactly(m):
    """update_many() phải cho vector R GIỐNG HỆT update() từng phần tử.

    Không phải "xấp xỉ giống" — phải khớp tuyệt đối, vì cả hai tính cùng một hàm
    băm SplitMix64 rồi lấy max. Nếu lệch dù một bit thì đường vector hóa sai.
    """
    import numpy as np
    rng = np.random.default_rng(0)
    items = rng.integers(0, 10 ** 9, size=5_000, dtype=np.int64)

    scalar = FlajoletMartin(m=m, g=1, seed=7)
    for it in items:
        scalar.update(int(it))

    batch = FlajoletMartin(m=m, g=1, seed=7)
    batch.update_many(items)

    assert scalar.R == batch.R
    assert scalar.estimate_loglog() == batch.estimate_loglog()


def test_update_many_is_order_and_chunk_independent():
    """Kết quả không phụ thuộc thứ tự hay cách chia lô — vì max có tính kết hợp.

    Đây là điều kiện để xử lý theo vi-lô (micro-batch) hợp lệ về mặt ngữ nghĩa luồng.
    """
    import numpy as np
    rng = np.random.default_rng(1)
    items = rng.integers(0, 10 ** 9, size=3_000, dtype=np.int64)

    a = FlajoletMartin(m=32, g=1, seed=3)
    a.update_many(items, chunk=64)

    b = FlajoletMartin(m=32, g=1, seed=3)
    b.update_many(items[::-1], chunk=4096)

    assert a.R == b.R


def test_update_many_handles_empty_and_zero():
    import numpy as np
    fm = FlajoletMartin(m=16, g=1, seed=5)
    fm.update_many(np.array([], dtype=np.int64))
    assert fm.estimate_loglog() >= 0
    fm.update_many(np.array([0, 0, 0], dtype=np.int64))
    assert fm._n_updates == 3
