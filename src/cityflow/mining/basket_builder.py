"""Xây giỏ hàng từ luồng chuyến đi — bước rời rạc hóa của tầng khai phá mẫu.

Quyết định thiết kế then chốt (Phase 4 §5.1):

    Giao dịch (basket) = một cửa sổ thời gian 15 phút
    Item                = "khu vực z đang ở trạng thái NHU CẦU CAO trong cửa sổ đó"

-------------------------------------------------------------------------------
VÌ SAO PHẢI CHUẨN HÓA THEO TỪNG KHU VỰC
-------------------------------------------------------------------------------
Nếu định nghĩa "hot" bằng NGƯỠNG TUYỆT ĐỐI (VD > 500 chuyến/15 phút), kết quả sẽ
tầm thường: các khu vực lớn luôn hot, các khu vực nhỏ KHÔNG BAO GIỜ hot và không
bao giờ xuất hiện trong bất kỳ luật nào. Tập luật thu được chỉ nói lại điều đã
biết là "Manhattan đông".

Thay vào đó, ngưỡng tính RIÊNG cho từng khu vực theo phân vị của chính nó:

    khu vực z hot trong cửa sổ w  <=>  count(z, w) > P_q({count(z, ·)})

Khi đó luật mang nghĩa "A bận HƠN BÌNH THƯỜNG thì C cũng bận HƠN BÌNH THƯỜNG" —
thông tin có thể hành động, và mọi khu vực đều có cơ hội xuất hiện.

Số liệu bổ trợ (docs/04_DATA_UNDERSTANDING §5): top 10 khu vực chỉ chiếm 13,3%
tổng số chuyến, không khu vực nào vượt 2%. Nên nguy cơ "kết quả tầm thường" nhẹ
hơn dự kiến, nhưng chênh lệch tuyệt đối giữa khu vực lớn nhất (374 nghìn chuyến)
và nhỏ nhất vẫn quá lớn để dùng ngưỡng chung.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class BasketSet:
    """Kết quả rời rạc hóa."""

    baskets: list[frozenset[int]]
    """Mỗi phần tử là tập khu vực 'hot' trong một cửa sổ."""

    window_starts: np.ndarray
    thresholds: dict[int, float]
    """Ngưỡng phân vị riêng của từng khu vực."""

    counts: np.ndarray
    """Ma trận (số cửa sổ, số khu vực) — số chuyến đón thô. Giữ lại để đối chiếu."""

    percentile: float

    @property
    def n_baskets(self) -> int:
        return len(self.baskets)

    def stats(self) -> dict:
        sizes = [len(b) for b in self.baskets]
        return {
            "n_baskets": len(self.baskets),
            "percentile": self.percentile,
            "mean_basket_size": float(np.mean(sizes)) if sizes else 0.0,
            "median_basket_size": float(np.median(sizes)) if sizes else 0.0,
            "max_basket_size": int(np.max(sizes)) if sizes else 0,
            "empty_baskets": int(sum(1 for s in sizes if s == 0)),
            "n_distinct_items": len({it for b in self.baskets for it in b}),
        }


def build_baskets(
    timestamps: np.ndarray,
    zones: np.ndarray,
    n_zones: int = 265,
    window_minutes: int = 15,
    percentile: float = 80.0,
    min_events_per_window: int = 100,
) -> BasketSet:
    """Rời rạc hóa luồng chuyến đi thành giỏ hàng.

    timestamps : datetime64, ĐÃ SẮP TĂNG DẦN
    zones      : mã khu vực đón, cùng độ dài với timestamps
    """
    if len(timestamps) == 0:
        return BasketSet([], np.array([]), {}, np.zeros((0, n_zones)), percentile)

    # --- Gán cửa sổ ---
    t = timestamps.astype("datetime64[s]").astype(np.int64)
    origin = t[0]
    win = (t - origin) // (window_minutes * 60)
    n_windows = int(win[-1]) + 1

    # --- Ma trận đếm (cửa sổ × khu vực) ---
    counts = np.zeros((n_windows, n_zones + 1), dtype=np.int32)
    np.add.at(counts, (win, zones.astype(np.int64)), 1)
    counts = counts[:, 1:]  # bỏ cột 0, khu vực đánh số từ 1

    # Loại cửa sổ quá thưa: thống kê trên cửa sổ vài chục sự kiện là nhiễu.
    keep = counts.sum(axis=1) >= min_events_per_window
    counts = counts[keep]
    window_starts = origin + np.flatnonzero(keep) * window_minutes * 60

    # --- Ngưỡng phân vị RIÊNG cho từng khu vực ---
    # Chỉ tính trên các cửa sổ khu vực đó có hoạt động: nếu tính cả cửa sổ bằng 0,
    # khu vực thưa sẽ có phân vị 80 bằng 0 và trở thành "hot" ở mọi cửa sổ có dù
    # chỉ một chuyến.
    thresholds: dict[int, float] = {}
    hot = np.zeros_like(counts, dtype=bool)
    for j in range(counts.shape[1]):
        col = counts[:, j]
        active = col[col > 0]
        if len(active) < 10:
            thresholds[j + 1] = float("inf")  # quá thưa để có ngưỡng đáng tin
            continue
        thr = float(np.percentile(active, percentile))
        thresholds[j + 1] = thr
        hot[:, j] = col > thr

    baskets = [frozenset((np.flatnonzero(row) + 1).tolist()) for row in hot]

    return BasketSet(baskets=baskets, window_starts=window_starts,
                     thresholds=thresholds, counts=counts, percentile=percentile)
