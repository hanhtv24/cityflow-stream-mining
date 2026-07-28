"""Oracle — tính CHÍNH XÁC số bit 1 trong cửa sổ trượt.

Nguyên tắc P3 (Phase 4 §3.2): oracle phải đi đường HOÀN TOÀN TÁCH BIỆT với tầng
sketch. Ở đây dùng tổng tiền tố (prefix sum) trên toàn bộ mảng — cách làm mà chính
DGIM sinh ra để tránh, vì nó cần O(n) bộ nhớ. Không dùng chung một dòng mã nào với
DGIM, nên không có nguy cơ "so sánh với chính mình".
"""

from __future__ import annotations

import numpy as np


class ExactWindowOracle:
    """Đếm chính xác bit 1 trong cửa sổ trượt bằng tổng tiền tố.

    Bộ nhớ O(n) — chấp nhận được vì oracle chạy offline, không phải thành phần
    của hệ thống luồng. Chính sự tương phản O(n) vs O(log^2 N) là điều cần đo.
    """

    __slots__ = ("_prefix", "n")

    def __init__(self, mask: np.ndarray) -> None:
        """mask: mảng bool, mask[i] = True nếu sự kiện thứ i+1 thỏa vị từ."""
        self.n = len(mask)
        # _prefix[i] = số bit 1 trong i sự kiện đầu tiên. _prefix[0] = 0.
        self._prefix = np.concatenate(([0], np.cumsum(mask, dtype=np.int64)))

    def count(self, t_now: int, k: int) -> int:
        """Số bit 1 chính xác trong k sự kiện gần nhất tính tới thời điểm t_now.

        t_now đánh số từ 1 (khớp với đồng hồ toàn cục của DGIM).
        """
        if t_now < 1:
            return 0
        t_now = min(t_now, self.n)
        start = max(0, t_now - k)
        return int(self._prefix[t_now] - self._prefix[start])

    def memory_bytes(self) -> int:
        return self._prefix.nbytes


class ExactWindowSumOracle:
    """Tổng chính xác các giá trị nguyên trong cửa sổ trượt (ground truth cho Q2)."""

    __slots__ = ("_prefix", "n")

    def __init__(self, values: np.ndarray) -> None:
        self.n = len(values)
        self._prefix = np.concatenate(([0], np.cumsum(values, dtype=np.int64)))

    def total(self, t_now: int, k: int) -> int:
        if t_now < 1:
            return 0
        t_now = min(t_now, self.n)
        start = max(0, t_now - k)
        return int(self._prefix[t_now] - self._prefix[start])

    def memory_bytes(self) -> int:
        return self._prefix.nbytes
