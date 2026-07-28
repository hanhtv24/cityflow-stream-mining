"""Kiểm định DGIM.

Nguyên tắc: MỖI VÍ DỤ SỐ TRONG SLIDE TRỞ THÀNH MỘT UNIT TEST. Vừa là kiểm định
tính đúng đắn, vừa là bằng chứng trực tiếp trong báo cáo rằng nhóm hiểu bài giảng.
"""

from __future__ import annotations

import random

import pytest

from cityflow.sketches.dgim import DGIM


# ---------------------------------------------------------------------------
# Tái hiện ví dụ trên slide
# ---------------------------------------------------------------------------


def _build_with_buckets(sizes_newest_first: list[int], N: int = 1000) -> DGIM:
    """Dựng DGIM có đúng tập bucket cho trước, để kiểm tra riêng quy tắc truy vấn.

    Gán timestamp giảm dần từ mới nhất (now) về cũ hơn.
    """
    from collections import deque

    d = DGIM(N=N, r=2)
    d.now = 100
    ts = 100
    for size in sizes_newest_first:
        e = size.bit_length() - 1
        while len(d.levels) <= e:
            d.levels.append(deque())
        d.levels[e].append(ts)  # append vào phải = vị trí cũ hơn
        ts -= 1
    return d


def test_slide_p65_estimate_is_6():
    """Slide tr.65: bucket 1,1,2,4 -> ước lượng = 1 + 1 + 2 + 4/2 = 6."""
    d = _build_with_buckets([1, 1, 2, 4])
    assert d.query() == 6


def test_slide_p61_estimate_is_12():
    """Slide tr.61: bucket 1,1,2,4,8 -> ước lượng = 1 + 1 + 2 + 4 + 8/2 = 12."""
    d = _build_with_buckets([1, 1, 2, 4, 8])
    assert d.query() == 12


def test_slide_p63_merge_cascade():
    """Slide tr.63: trạng thái 1,1,2,4 nhận thêm bit 1.

    Bước 1: xuất hiện 3 bucket cỡ 1 -> gộp 2 bucket CŨ NHẤT thành 1 bucket cỡ 2.
    Kết quả: 1,2,2,4.

    LƯU Ý về một điểm không nhất quán trong slide: tr.63 viết tiếp "Có 2 bucket
    cỡ 2: tiếp tục gộp đệ quy thành 1 bucket cỡ 4". Nhưng bất biến nêu ở tr.60 là
    "Tối đa 1 HOẶC 2 bucket cùng kích thước" — nên trạng thái 1,2,2,4 là HỢP LỆ và
    KHÔNG cần gộp tiếp. Cài đặt này theo bất biến tr.60 (gộp khi số bucket vượt r).
    Với r=2, phép gộp thứ hai chỉ xảy ra khi xuất hiện bucket cỡ 2 thứ ba.
    """
    d = _build_with_buckets([1, 1, 2, 4])
    d.record(101)
    assert d.bucket_sizes() == [1, 2, 2, 4]

    # Bucket cỡ 2 thứ ba mới kích hoạt gộp tầng tiếp theo.
    d2 = _build_with_buckets([1, 1, 2, 2])
    d2.record(101)
    assert d2.bucket_sizes() == [1, 2, 4]


# ---------------------------------------------------------------------------
# Bất biến của cấu trúc (slide tr.60)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("r", [2, 4, 8, 16])
def test_invariant_max_r_buckets_per_size(r):
    """Bất biến 1: tối đa r bucket cùng kích thước."""
    rng = random.Random(7)
    d = DGIM(N=10_000, r=r)
    for _ in range(50_000):
        d.update(rng.random() < 0.3)
        for level in d.levels:
            assert len(level) <= r


def test_invariant_sizes_nondecreasing_with_age():
    """Bất biến 3: bucket mới nhỏ hơn (hoặc bằng) bucket cũ hơn."""
    rng = random.Random(11)
    d = DGIM(N=5_000, r=2)
    for _ in range(30_000):
        d.update(rng.random() < 0.4)
    sizes = d.bucket_sizes()  # mới -> cũ
    assert sizes == sorted(sizes), f"kích thước không tăng dần theo tuổi: {sizes}"


def test_invariant_timestamps_strictly_decreasing():
    """Bất biến 2: các bucket không chồng lấn timestamp."""
    rng = random.Random(13)
    d = DGIM(N=5_000, r=2)
    for _ in range(30_000):
        d.update(rng.random() < 0.4)
    all_ts = [ts for level in d.levels for ts in level]
    assert len(all_ts) == len(set(all_ts)), "có timestamp trùng giữa các bucket"


# ---------------------------------------------------------------------------
# Cận sai số 50% (slide tr.64)
# ---------------------------------------------------------------------------


def _exact_count(bits: list[int], k: int) -> int:
    return sum(bits[-k:])


@pytest.mark.parametrize("density", [0.05, 0.2, 0.5, 0.8])
@pytest.mark.parametrize("r", [2, 4, 8])
def test_error_bound_50_percent(density, r):
    """Sai số tương đối phải <= 50% với mọi mật độ bit 1 và mọi r."""
    rng = random.Random(hash((density, r)) & 0xFFFF)
    N = 2_000
    bits = [1 if rng.random() < density else 0 for _ in range(20_000)]

    d = DGIM(N=N, r=r)
    for b in bits:
        d.update(b)

    exact = _exact_count(bits, N)
    est = d.query()
    assert exact > 0
    rel_err = abs(est - exact) / exact
    assert rel_err <= 0.5, f"vi phạm cận 50%: est={est} exact={exact} err={rel_err:.3f}"


def test_error_decreases_with_r():
    """Sai số giảm khi tăng r — quan hệ O(1/r), slide tr.64.

    Kiểm tra xu hướng trên nhiều hạt giống ngẫu nhiên: sai số trung bình của r=16
    phải thấp hơn hẳn r=2 (r=2 là cấu hình nhỏ nhất hợp lệ, xem test_r_below_2).
    """
    N = 2_000
    mean_errors = {}
    for r in (2, 4, 8, 16):
        errs = []
        for seed in range(20):
            rng = random.Random(seed)
            bits = [1 if rng.random() < 0.3 else 0 for _ in range(20_000)]
            d = DGIM(N=N, r=r)
            for b in bits:
                d.update(b)
            exact = _exact_count(bits, N)
            errs.append(abs(d.query() - exact) / exact)
        mean_errors[r] = sum(errs) / len(errs)

    assert mean_errors[16] < mean_errors[2], f"sai số không giảm theo r: {mean_errors}"
    assert mean_errors[8] <= mean_errors[2], f"xu hướng bất thường: {mean_errors}"


# ---------------------------------------------------------------------------
# Trường hợp biên
# ---------------------------------------------------------------------------


def test_empty_stream_returns_zero():
    assert DGIM(N=100).query() == 0


def test_all_zeros_returns_zero():
    d = DGIM(N=100)
    for _ in range(1_000):
        d.update(0)
    assert d.query() == 0


def test_all_ones_is_near_exact():
    """Luồng toàn bit 1: đáp án đúng là N, sai số phải nhỏ."""
    N = 1_000
    d = DGIM(N=N)
    for _ in range(10_000):
        d.update(1)
    assert abs(d.query() - N) / N <= 0.5


def test_fewer_ones_than_window_is_exact_enough():
    """Nếu tổng số bit 1 ít hơn số bucket cho phép, ước lượng gần như chính xác."""
    d = DGIM(N=1_000, r=2)
    for i in range(1_000):
        d.update(1 if i % 500 == 0 else 0)
    assert d.query() in (1, 2)  # 2 bit 1, có thể trừ nửa bucket cũ nhất


def test_query_k_smaller_than_N():
    """Truy vấn với k < N phải cho kết quả không lớn hơn truy vấn với N."""
    rng = random.Random(3)
    d = DGIM(N=10_000, r=2)
    for _ in range(50_000):
        d.update(rng.random() < 0.3)
    assert d.query(k=1_000) <= d.query(k=10_000)


def test_expiry_drops_old_buckets():
    """Bit 1 cũ hơn N phải bị loại khỏi ước lượng (bất biến 4)."""
    d = DGIM(N=100, r=2)
    for _ in range(50):
        d.update(1)
    for _ in range(200):  # đẩy toàn bộ bit 1 ra khỏi cửa sổ
        d.update(0)
    assert d.query() == 0


# ---------------------------------------------------------------------------
# Đồng hồ toàn cục (đường đi dùng trong SketchRegistry)
# ---------------------------------------------------------------------------


def test_record_with_global_clock_matches_update():
    """record(t) với đồng hồ ngoài phải cho kết quả y hệt update(bit).

    Đây là đường đi mà SketchRegistry sử dụng để tránh lặp qua 535 luồng mỗi sự kiện.
    """
    rng = random.Random(17)
    bits = [1 if rng.random() < 0.3 else 0 for _ in range(20_000)]

    a = DGIM(N=2_000, r=2)
    for b in bits:
        a.update(b)

    b_sketch = DGIM(N=2_000, r=2)
    for t, bit in enumerate(bits, start=1):
        if bit:
            b_sketch.record(t)
    b_sketch.now = len(bits)  # đồng hồ toàn cục tiến kể cả khi không có bit 1

    assert a.bucket_sizes() == b_sketch.bucket_sizes()
    assert a.query() == b_sketch.query()


def test_stream_with_no_events_is_safe():
    """3/265 khu vực không có sự kiện đón nào (xem 04_DATA_UNDERSTANDING §2.3).

    Truy vấn trên luồng rỗng với đồng hồ toàn cục đã tiến xa phải trả 0, không lỗi.
    """
    d = DGIM(N=1_000_000, r=2)
    assert d.query(t_now=19_663_930) == 0
    assert d.n_buckets() == 0


# ---------------------------------------------------------------------------
# Bộ nhớ (nguyên tắc P2)
# ---------------------------------------------------------------------------


def test_memory_grows_logarithmically():
    """Bộ nhớ phải tăng theo log(N), không theo N.

    Đây là toàn bộ lý do tồn tại của DGIM: N tăng 1000 lần thì bộ nhớ chỉ tăng vài lần.
    """
    rng = random.Random(23)
    bits = [1 if rng.random() < 0.3 else 0 for _ in range(200_000)]

    mem = {}
    for N in (1_000, 10_000, 100_000):
        d = DGIM(N=N, r=2)
        for b in bits:
            d.update(b)
        mem[N] = d.memory_bytes()

    growth = mem[100_000] / mem[1_000]
    assert growth < 5, f"bộ nhớ tăng quá nhanh theo N: {mem}"


def test_memory_far_below_exact_window():
    """Bộ nhớ DGIM phải nhỏ hơn lưu cửa sổ đầy đủ.

    Đo được (N=10^6, r=2, 2 triệu sự kiện, mật độ 0.3):
        cửa sổ đầy đủ dạng bit array : 125.000 byte
        DGIM đo thật trong Python    :  15.500 byte  ->  nhỏ hơn  8x
        DGIM theo cận lý thuyết      :     121 byte  ->  nhỏ hơn 1030x

    Khoảng cách giữa 8x và 1030x là CHI PHÍ ĐỐI TƯỢNG CỦA PYTHON: mỗi timestamp là
    một int 28 byte thay vì log2(N)=20 bit, và mỗi deque tốn ~500 byte overhead.
    Ưu thế tiệm cận chỉ áp đảo khi N đủ lớn. Đây là phát hiện phải báo cáo trung
    thực ở thực nghiệm E3, không phải giấu đi: cận O(log^2 N) nói về ĐỘ TĂNG TRƯỞNG,
    không hứa hằng số nhỏ trong một ngôn ngữ có overhead cao.
    """
    N = 1_000_000
    rng = random.Random(29)
    d = DGIM(N=N, r=2)
    for _ in range(2_000_000):
        d.update(rng.random() < 0.3)

    exact_window_bytes = N / 8  # 1 bit/phần tử
    assert d.memory_bytes() < exact_window_bytes / 5
    # Cận lý thuyết phải nhỏ hơn thực tế Python nhiều lần — xác nhận nguồn gốc khoảng cách.
    assert d.theoretical_bits() / 8 < d.memory_bytes() / 10


def test_r_below_2_is_rejected():
    """r=1 là cấu hình suy biến và phải bị từ chối ngay ở constructor.

    Slide tr.64 mô tả sơ đồ "duy trì r HOẶC r-1 bucket mỗi kích thước", nên r=1
    nghĩa là "0 hoặc 1 bucket" — toàn bộ luồng dồn vào một bucket kế thừa timestamp
    của bit 1 gần nhất, khiến nó không bao giờ hết hạn.

    Đo được trước khi thêm ràng buộc này: N=2000, mật độ 0.05
        đáp án đúng = 100, ước lượng = 514  (sai số 414%, vi phạm cận 50%)
    """
    with pytest.raises(ValueError, match="r phải >= 2"):
        DGIM(N=1_000, r=1)
