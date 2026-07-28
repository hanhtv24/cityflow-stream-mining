"""AMS (Alon-Matias-Szegedy) — ước lượng mô-men của luồng.

Cài đặt from scratch theo slide chương Data Streaming tr.46-51.

Mô-men bậc n của luồng S:  sum_{i in S} (m_i)^n, với m_i là số lần phần tử i xuất hiện.
    - Bậc 0: số phần tử phân biệt
    - Bậc 1: độ dài luồng
    - Bậc 2: SỐ BẤT NGỜ (surprise number) — đo mức độ không đồng đều của phân phối

Slide tr.45: "Số bất ngờ lớn => phân phối lệch. Ứng dụng: phát hiện điểm bất
thường (anomaly), tắc nghẽn mạng."

Thuật toán (tr.46):
    1. Chọn ngẫu nhiên vị trí i từ 1 đến n
    2. Khi luồng đến vị trí i: X.val = s_i, X.c = 1
    3. Mỗi lần gặp lại X.val về sau: X.c += 1

Ước lượng bậc 2 (tr.47):        f_hat = n(2·X.c - 1)
Tổng quát bậc k (tr.50):        f_hat = n(c^k - (c-1)^k)
Với k biến, lấy trung bình để giảm phương sai.

Khi n KHÔNG biết trước (tr.51): dùng Reservoir Sampling chọn vị trí, và dùng độ
dài hiện tại của luồng làm n trong công thức ước lượng.
"""

from __future__ import annotations

import random
import statistics
import sys
from collections import defaultdict

from .base import Sketch


class AMS(Sketch):
    """Ước lượng mô-men bậc k của luồng bằng k biến ngẫu nhiên.

    Ghi chú hiệu năng: cách cài ngây thơ phải quét cả k biến mỗi phần tử để tìm
    biến nào có val trùng — O(k) mỗi sự kiện, tức 100 x 19,7 triệu = 2 tỷ phép so
    sánh. Ở đây dùng chỉ mục nghịch đảo val -> danh sách chỉ số biến, cho O(1)
    khấu hao mỗi sự kiện.
    """

    __slots__ = ("k", "n", "vals", "counts", "_index", "_rng")

    def __init__(self, k: int = 100, seed: int = 42) -> None:
        if k < 1:
            raise ValueError("k phải >= 1")
        self.k = k
        self.n = 0
        self.vals: list = [None] * k
        self.counts: list[int] = [0] * k
        self._index: dict = defaultdict(list)  # val -> [chỉ số biến]
        self._rng = random.Random(seed)

    def update(self, item) -> None:
        """Nạp một phần tử của luồng."""
        self.n += 1

        # Bước 3: mọi biến đang theo dõi item này đều tăng đếm.
        for idx in self._index.get(item, ()):
            self.counts[idx] += 1

        if self.n <= self.k:
            # Bước 1-2: k vị trí đầu tiên nhận k biến (slide tr.51).
            idx = self.n - 1
            self.vals[idx] = item
            self.counts[idx] = 1
            self._index[item].append(idx)
            return

        # Reservoir Sampling: nhận phần tử mới làm biến mới với xác suất k/n.
        if self._rng.random() < self.k / self.n:
            idx = self._rng.randrange(self.k)
            old = self.vals[idx]
            if old is not None:
                lst = self._index[old]
                lst.remove(idx)
                if not lst:
                    del self._index[old]
            self.vals[idx] = item
            self.counts[idx] = 1
            self._index[item].append(idx)

    def estimate_moment(self, order: int = 2) -> float:
        """Ước lượng mô-men bậc `order`.

        order=2 -> n(2c - 1)          (slide tr.47)
        tổng quát -> n(c^k - (c-1)^k)  (slide tr.50)
        """
        active = [c for c in self.counts if c > 0]
        if not active:
            return 0.0
        if order == 2:
            terms = [self.n * (2 * c - 1) for c in active]
        else:
            terms = [self.n * (c ** order - (c - 1) ** order) for c in active]
        return statistics.fmean(terms)

    def surprise_number(self) -> float:
        """Bí danh của mô-men bậc 2 — thuật ngữ slide tr.45."""
        return self.estimate_moment(2)

    def memory_bytes(self) -> int:
        total = sys.getsizeof(self.vals) + sys.getsizeof(self.counts)
        total += sum(sys.getsizeof(v) for v in self.vals if v is not None)
        total += sum(sys.getsizeof(c) for c in self.counts)
        total += sys.getsizeof(self._index)
        return total

    def theoretical_bits(self) -> float:
        """O(k): mỗi biến lưu một val và một bộ đếm."""
        return self.k * 2 * 64.0

    def __repr__(self) -> str:
        return f"AMS(k={self.k}, n={self.n:,}, surprise={self.surprise_number():,.0f})"


def exact_moment(items, order: int = 2) -> int:
    """Mô-men chính xác — oracle độc lập, KHÔNG dùng chung mã với AMS."""
    freq: dict = defaultdict(int)
    for it in items:
        freq[it] += 1
    return sum(m ** order for m in freq.values())
