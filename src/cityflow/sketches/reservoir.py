"""Reservoir Sampling — giữ mẫu kích thước cố định từ luồng vô hạn.

Cài đặt from scratch theo slide chương Data Streaming tr.18-21.

Thuật toán:
    1. Lưu s phần tử đầu tiên vào hồ chứa
    2. Khi phần tử thứ n đến (n > s):
       - Với xác suất s/n : giữ phần tử mới, thay thế ngẫu nhiên 1 phần tử trong hồ
       - Với xác suất 1 - s/n: bỏ qua

Bảo đảm: sau n phần tử, MỖI phần tử đã đi qua có xác suất đúng s/n nằm trong mẫu.

Chứng minh quy nạp (slide tr.20-21):
    Cơ sở: s phần tử đầu có xác suất s/s = 1
    Bước:  xác suất phần tử n+1 ở lại mẫu
              = (1 - s/(n+1))          [không được chọn]
              + s/(n+1) · (s-1)/s      [được chọn nhưng không bị thay]
              = n/(n+1)
           phần tử cũ có xác suất s/n, sống sót với xác suất n/(n+1):
              s/n · n/(n+1) = s/(n+1)  ✓
"""

from __future__ import annotations

import random
import sys

from .base import Sketch


class ReservoirSampler(Sketch):
    """Giữ đúng s phần tử đại diện, mỗi phần tử của luồng có xác suất bằng nhau."""

    __slots__ = ("s", "reservoir", "n", "_rng")

    def __init__(self, s: int = 100_000, seed: int = 42) -> None:
        if s < 1:
            raise ValueError("s phải >= 1")
        self.s = s
        self.reservoir: list = []
        self.n = 0
        self._rng = random.Random(seed)

    def update(self, item) -> None:
        self.n += 1
        if len(self.reservoir) < self.s:
            self.reservoir.append(item)
            return
        # Xác suất s/n giữ phần tử mới.
        j = self._rng.randrange(self.n)
        if j < self.s:
            self.reservoir[j] = item

    def sample(self) -> list:
        return list(self.reservoir)

    def memory_bytes(self) -> int:
        return sys.getsizeof(self.reservoir) + sum(sys.getsizeof(x) for x in self.reservoir)

    def theoretical_bits(self) -> float:
        return self.s * 64.0

    def __repr__(self) -> str:
        return f"ReservoirSampler(s={self.s:,}, n={self.n:,})"


class HashBasedSampler(Sketch):
    """Lấy mẫu theo KHÓA bằng hàm băm — slide tr.17.

    Giữ toàn bộ bản ghi của một tỷ lệ a/b các khóa, thay vì một tỷ lệ các bản ghi.

    Vì sao cần: slide tr.16 chứng minh bằng đại số rằng lấy mẫu SAI ĐƠN VỊ cho ước
    lượng CHỆCH. Với câu hỏi "tỷ lệ truy vấn trùng lặp", lấy mẫu theo bản ghi cho
    b/(10a + 19b) trong khi đáp án đúng là b/(a + b).

    Bài học của slide: "Phải cẩn thận chọn đúng đơn vị lấy mẫu tùy theo bài toán."
    Thực nghiệm E8 tái hiện bài học này trên dữ liệu CityFlow thật.
    """

    __slots__ = ("a", "b", "kept", "n_seen", "n_kept")

    def __init__(self, a: int = 3, b: int = 10) -> None:
        if not 0 < a <= b:
            raise ValueError("cần 0 < a <= b")
        self.a = a
        self.b = b
        self.kept: list = []
        self.n_seen = 0
        self.n_kept = 0

    @property
    def sampling_rate(self) -> float:
        return self.a / self.b

    def _keep_key(self, key) -> bool:
        # Băm khóa đồng đều vào b bucket, giữ nếu giá trị băm < a.
        from .flajolet_martin import _splitmix64
        return _splitmix64(hash(key) & ((1 << 64) - 1)) % self.b < self.a

    def update(self, key, record=None) -> None:
        self.n_seen += 1
        if self._keep_key(key):
            self.n_kept += 1
            self.kept.append(record if record is not None else key)

    def memory_bytes(self) -> int:
        return sys.getsizeof(self.kept) + sum(sys.getsizeof(x) for x in self.kept)

    def theoretical_bits(self) -> float:
        return len(self.kept) * 64.0

    def __repr__(self) -> str:
        return (f"HashBasedSampler(rate={self.sampling_rate:.0%}, "
                f"kept={self.n_kept:,}/{self.n_seen:,})")
