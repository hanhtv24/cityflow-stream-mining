"""DGIM mở rộng — ước lượng TỔNG các số nguyên trong cửa sổ trượt.

Cài đặt theo slide chương Data Streaming tr.66:

    "Tổng của k số nguyên gần nhất: mỗi số nguyên có tối đa m bit · Coi mỗi bit
     như một luồng riêng và đếm bit 1 trong k phần tử gần nhất · Ước lượng
     sum_{i=0}^{m-1} c_i * 2^i, trong đó c_i là ước lượng DGIM cho bit thứ i."

Không nhóm nào trong lớp dùng phần mở rộng này (xem docs/01_PHAN_TICH_DE_TAI_CAC_NHOM.md §6.1).

---------------------------------------------------------------------------
CÂU HỎI NGHIÊN CỨU RIÊNG CỦA ĐỀ TÀI — GIẢ THUYẾT H1
---------------------------------------------------------------------------

Slide không nói gì về việc PHÂN BỔ ngân sách bộ nhớ giữa m luồng bit. Cách hiển
nhiên là cho mọi luồng cùng một r. Nhưng sai số của mỗi luồng bit bị nhân với
trọng số 2^i rất khác nhau, nên phân bổ đều khó có thể tối ưu.

Phân tích: sai số tuyệt đối của DGIM trên luồng bit i xấp xỉ B_i/2, với B_i là
kích thước bucket cũ nhất. Theo bất biến, c_i >~ r_i * B_i, nên B_i ~ c_i / r_i:

    sai số tuyệt đối của luồng bit i  ~  c_i / (2 * r_i)

Đóng góp vào sai số của TỔNG (do trọng số 2^i):

    E  ~  sum_i  2^i * c_i / (2 * r_i)

Cực tiểu hóa E với ràng buộc ngân sách sum_i r_i = R. Nhân tử Lagrange:

    d/dr_i [ 2^i * c_i / (2 r_i) ]  =  -2^i * c_i / (2 r_i^2)  =  -lambda

    =>  r_i  ∝  sqrt( 2^i * c_i )                                        (*)

H1: phân bổ theo (*) cho sai số thấp hơn phân bổ đều ở CÙNG ngân sách sum(r_i).

Lưu ý quan trọng: công thức (*) KHÔNG đơn giản nói "cho bit cao nhiều r hơn".
Nó cân bằng giữa trọng số 2^i (tăng theo i) và tần suất c_i (giảm theo i vì giá
trị lớn hiếm). Điểm tối ưu có thể rơi vào các bit GIỮA. Đây là điều thực nghiệm
E4 phải trả lời bằng dữ liệu thật.
"""

from __future__ import annotations

import math

import numpy as np

from .base import Sketch
from .dgim import DGIM


class DGIMInteger(Sketch):
    """Ước lượng tổng các giá trị nguyên trong cửa sổ N phần tử gần nhất.

    Mỗi giá trị được tách thành m bit; bit thứ i được nạp vào một DGIM riêng.
    """

    __slots__ = ("N", "m", "r_alloc", "streams", "now", "_clipped")

    def __init__(self, N: int, m: int = 8, r: int | None = 2,
                 r_alloc: list[int] | tuple[int, ...] | None = None) -> None:
        """
        r        : dùng chung cho mọi luồng bit (phân bổ ĐỀU)
        r_alloc  : r riêng cho từng vị trí bit, độ dài m (phân bổ KHÔNG ĐỀU)
                   Nếu truyền r_alloc thì r bị bỏ qua.
        """
        if r_alloc is not None:
            if len(r_alloc) != m:
                raise ValueError(f"r_alloc phải có đúng {m} phần tử, nhận {len(r_alloc)}")
            self.r_alloc = tuple(r_alloc)
        else:
            self.r_alloc = tuple([r] * m)

        self.N = N
        self.m = m
        self.now = 0
        self._clipped = 0
        self.streams = [DGIM(N=N, r=self.r_alloc[i]) for i in range(m)]

    @property
    def max_value(self) -> int:
        return (1 << self.m) - 1

    def update(self, value: int) -> None:
        """Nạp một giá trị, tự tăng đồng hồ nội bộ."""
        self.now += 1
        self.record(self.now, value)

    def record(self, t: int, value: int) -> None:
        """Nạp giá trị tại vị trí t của đồng hồ toàn cục."""
        self.now = t
        if value > self.max_value:
            self._clipped += 1
            value = self.max_value
        elif value < 0:
            value = 0
        # Chỉ chạm vào các luồng bit có bit 1 — slide tr.62.
        i = 0
        v = int(value)
        while v:
            if v & 1:
                self.streams[i].record(t)
            v >>= 1
            i += 1

    def query(self, k: int | None = None, t_now: int | None = None) -> int:
        """Ước lượng tổng: sum_i c_i * 2^i (slide tr.66)."""
        t_now = self.now if t_now is None else t_now
        return sum(s.query(k, t_now) << i for i, s in enumerate(self.streams))

    def query_per_bit(self, k: int | None = None, t_now: int | None = None) -> list[int]:
        """Ước lượng c_i của từng luồng bit — dùng để phân rã sai số (E4)."""
        t_now = self.now if t_now is None else t_now
        return [s.query(k, t_now) for s in self.streams]

    def n_clipped(self) -> int:
        return self._clipped

    def total_r_budget(self) -> int:
        """Tổng ngân sách bucket — đại lượng giữ cố định khi so sánh các phân bổ."""
        return sum(self.r_alloc)

    def memory_bytes(self) -> int:
        return sum(s.memory_bytes() for s in self.streams)

    def theoretical_bits(self) -> float:
        return sum(s.theoretical_bits() for s in self.streams)

    def __repr__(self) -> str:
        return f"DGIMInteger(N={self.N:,}, m={self.m}, r_alloc={self.r_alloc})"


# ---------------------------------------------------------------------------
# Chiến lược phân bổ ngân sách
# ---------------------------------------------------------------------------


def uniform_allocation(m: int, budget: int) -> list[int]:
    """Phân bổ đều — cách làm hiển nhiên, dùng làm mốc so sánh (baseline)."""
    base = budget // m
    rem = budget - base * m
    alloc = [max(2, base)] * m
    for i in range(rem):
        alloc[i % m] += 1
    return alloc


def sqrt_weighted_allocation(m: int, budget: int, bit_counts: np.ndarray) -> list[int]:
    """Phân bổ theo công thức (*): r_i tỉ lệ với sqrt(2^i * c_i).

    bit_counts[i] = số sự kiện có bit thứ i bằng 1 (đếm trên dữ liệu thật).
    Mọi r_i được ép >= 2 vì r=1 là cấu hình suy biến (xem dgim.DGIM.__init__).
    """
    weights = np.sqrt(np.array([(1 << i) * max(int(bit_counts[i]), 1) for i in range(m)],
                               dtype=np.float64))
    weights = weights / weights.sum()

    alloc = np.maximum(2, np.floor(weights * budget).astype(int))
    # Cân lại cho khớp đúng ngân sách sau khi ép sàn.
    while alloc.sum() > budget and (alloc > 2).any():
        alloc[int(np.argmax(alloc))] -= 1
    while alloc.sum() < budget:
        alloc[int(np.argmax(weights - alloc / max(alloc.sum(), 1)))] += 1
    return alloc.tolist()


def high_bit_allocation(m: int, budget: int) -> list[int]:
    """Phân bổ tăng dần theo vị trí bit — dạng NGÂY THƠ của H1.

    Đây là điều trực giác mách bảo ("bit cao quan trọng hơn vì trọng số 2^i lớn"),
    nhưng nó bỏ qua việc c_i giảm theo i. E4 sẽ cho biết trực giác này đúng hay sai.
    """
    weights = np.arange(1, m + 1, dtype=np.float64)
    weights = weights / weights.sum()
    alloc = np.maximum(2, np.floor(weights * budget).astype(int))
    while alloc.sum() > budget and (alloc > 2).any():
        alloc[int(np.argmax(alloc))] -= 1
    while alloc.sum() < budget:
        alloc[int(np.argmin(alloc))] += 1
    return alloc.tolist()


def compute_bit_counts(values: np.ndarray, m: int) -> np.ndarray:
    """Đếm số lần mỗi vị trí bit bằng 1 trên toàn bộ tập giá trị."""
    return np.array([int(((values >> i) & 1).sum()) for i in range(m)], dtype=np.int64)


def predicted_error_weight(alloc: list[int], bit_counts: np.ndarray, m: int) -> float:
    """Sai số dự đoán theo mô hình  E ~ sum_i 2^i * c_i / (2 r_i).

    Dùng để đối chiếu mô hình lý thuyết với sai số đo thật.
    """
    return sum((1 << i) * int(bit_counts[i]) / (2 * alloc[i]) for i in range(m))


def bits_needed(max_value: float) -> int:
    return max(1, math.ceil(math.log2(max(max_value, 1) + 1)))
