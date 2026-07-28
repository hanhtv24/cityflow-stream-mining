"""Flajolet-Martin — đếm số phần tử phân biệt với bộ nhớ O(m·log N).

Cài đặt from scratch theo slide chương Data Streaming tr.37-41.

Thuật toán:
    1. Chọn hàm băm h ánh xạ phần tử thành ít nhất log2(N) bit
    2. Với mỗi phần tử s, tính r(s) = số số 0 ở CUỐI biểu diễn nhị phân
    3. Duy trì R = max_s r(s)
    4. Ước lượng số phần tử phân biệt ~ 2^R

Trực giác (tr.39): với hàm băm đều, tỷ lệ 2^-r phần tử có ít nhất r số 0 ở cuối,
nên cần khoảng 2^r phần tử phân biệt để xuất hiện một phần tử có r số 0 cuối.

Nhược điểm và cách khắc phục (tr.40):
    - Ước lượng đơn có phương sai rất lớn
    - Trung bình      -> nhạy với ngoại lệ (2^R tăng theo cấp số nhân)
    - Trung vị        -> ổn định hơn, NHƯNG kết quả luôn là lũy thừa của 2
    - Tốt nhất        -> chia m hàm băm thành g nhóm, lấy TRUNG BÌNH trong mỗi nhóm
                         rồi lấy TRUNG VỊ của các trung bình đó
"""

from __future__ import annotations

import random
import statistics
import sys

from .base import Sketch

_MASK64 = (1 << 64) - 1

# --- Hệ số hiệu chuẩn --------------------------------------------------------
#
# Hằng số phi = 0,77351 của Flajolet & Martin (1985) KHÔNG áp dụng được cho sơ đồ
# này. Phi được suy ra cho biến thể "stochastic averaging" — chia luồng vào các
# bucket theo bit cao rồi lấy max trong từng bucket. Sơ đồ mà slide tr.40 mô tả
# khác hẳn: m hàm băm ĐỘC LẬP, mỗi hàm lấy max trên TOÀN BỘ luồng.
#
# Đo thực nghiệm (m=64, g=8, 25 hạt giống, true_n thuộc {1k, 5k, 20k, 80k}) cho
# thấy mỗi chiến lược tổng hợp có một bội số chệch RIÊNG và ỔN ĐỊNH:
#
#     chiến lược          bội số chệch    dao động        độ ổn định
#     mean                    3,8416      3,50..4,69      ±15%   (tệ nhất)
#     median_of_means         2,3168      2,29..2,59       ±6%
#     median                  0,8192      0,82..1,02      ±12%   (nhảy bậc lũy thừa 2)
#     loglog                  1,6037      1,56..1,63       ±2%   (ổn định nhất)
#
# Vì bội số ổn định qua nhiều bậc độ lớn, nó hiệu chỉnh được bằng một hằng số —
# đúng cách mà HyperLogLog xử lý bằng các hằng số alpha_m của nó.
#
# Áp dụng phi = 0,77351 vào sơ đồ này khiến sai số TỆ ĐI (nhân thêm 1,29 lần trong
# khi ước lượng vốn đã thừa 2,3 lần). Xem docs/07_KET_QUA_E5_E6.md.

PHI_LITERATURE = 0.77351
"""Hằng số kinh điển — giữ lại để đối chứng, KHÔNG dùng cho sơ đồ này."""

CALIBRATION = {
    "mean": 3.8416,
    "median": 0.8192,
    "median_of_means": 2.3168,
}
"""Bội số chệch THÔ, đo tại m=64, g=8. Ước lượng đã hiệu chuẩn = thô / hằng số."""

# --- Hằng số riêng cho loglog, phụ thuộc m -----------------------------------
#
# Thực nghiệm E5b cho thấy hiệu chuẩn bằng MỘT hằng số duy nhất khiến sai số KHÔNG
# giảm đơn điệu theo m (16,6% -> 22,7% -> 24,0% tại m = 64, 128, 256) trong khi hệ
# số biến thiên vẫn giảm đều (16,2% -> 13,4% -> 6,3%). Phương sai giảm nhưng độ
# chệch đổi theo m, nên hằng số cố định làm hỏng phần lợi thu được.
#
# Hiệu chuẩn lại RIÊNG cho từng m (dữ liệu tổng hợp, true_n thuộc {5k, 20k, 80k},
# 8 hạt giống) khôi phục tính đơn điệu — xem docs/07_KET_QUA_E5_E6.md.
#
# Lưu ý: hằng số được hiệu chuẩn trên dữ liệu TỔNG HỢP, không dùng dữ liệu NYC TLC,
# để tránh rò rỉ thông tin từ tập đánh giá sang tham số.

ALPHA_M_LOGLOG = {
    8: 1.0183, 16: 1.2634, 32: 1.3052, 64: 1.2098, 128: 1.2330, 256: 1.2772,
}
DEFAULT_ALPHA_LOGLOG = 1.2405
"""Dùng khi m không nằm trong bảng đã hiệu chuẩn."""


def _splitmix64(z: int) -> int:
    """Hàm trộn bit của SplitMix64 — khuếch tán mạnh trên TOÀN BỘ 64 bit.

    Vì sao KHÔNG dùng dạng affine (a*x + b) mod 2^64 như slide tr.22 gợi ý cho
    MinHash: trong số học mod 2^k, bit thấp của tích a*x chỉ phụ thuộc bit thấp
    của x — cụ thể bit 0 của kết quả luôn bằng bit 0 của x khi a lẻ. Mà Flajolet-
    Martin đếm số 0 Ở CUỐI, tức phụ thuộc hoàn toàn vào chính các bit thấp đó.
    Dùng hàm affine mod 2^64 sẽ khiến r(s) gần như không ngẫu nhiên.

    (Dạng affine mod p với p NGUYÊN TỐ thì không mắc vấn đề này, nhưng chậm hơn
    trong Python vì phải chia lấy dư số lớn.)
    """
    z = (z + 0x9E3779B97F4A7C15) & _MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
    return (z ^ (z >> 31)) & _MASK64


class FlajoletMartin(Sketch):
    """Ước lượng số phần tử phân biệt trong luồng."""

    __slots__ = ("m", "g", "R", "_seeds", "_n_updates")

    def __init__(self, m: int = 64, g: int = 8, seed: int = 42) -> None:
        if m < 1:
            raise ValueError("m phải >= 1")
        if g < 1 or g > m:
            raise ValueError(f"g phải trong [1, m={m}], nhận {g}")
        if m % g != 0:
            raise ValueError(f"m={m} phải chia hết cho g={g} để các nhóm bằng nhau")

        self.m = m
        self.g = g
        rng = random.Random(seed)
        self._seeds = [rng.getrandbits(64) for _ in range(m)]
        self.R = [0] * m
        self._n_updates = 0

    @staticmethod
    def _trailing_zeros(h: int) -> int:
        """r(s) — số số 0 ở cuối biểu diễn nhị phân (slide tr.37).

        Ví dụ slide: h(s) = 12 = 1100_2 -> 2 số 0 ở cuối -> r(s) = 2.
        """
        if h == 0:
            return 64
        return (h & -h).bit_length() - 1

    def update(self, item: int) -> None:
        """Nạp một phần tử. item phải là số nguyên (VD route_id = pu*1000 + do)."""
        self._n_updates += 1
        for j in range(self.m):
            r = self._trailing_zeros(_splitmix64(item ^ self._seeds[j]))
            if r > self.R[j]:
                self.R[j] = r

    def update_many(self, items, chunk: int = 8192) -> None:
        """Nạp một lô phần tử — vector hóa toàn bộ m hàm băm bằng numpy.

        VÌ SAO CẦN: thực nghiệm E7 đo được Flajolet-Martin với m=256 chiếm 97,2%
        tổng thời gian xử lý, trong khi toàn bộ 535 luồng DGIM chỉ chiếm ~1,5%.
        Nguyên nhân là m phép băm cho MỖI sự kiện trong vòng lặp Python thuần.
        Cấu hình m=256 mà E5 chọn vì độ chính xác lại đắt gấp 36 lần m=8 về tính toán.

        Vector hóa tính cả m giá trị băm cho cả lô trong một phép numpy duy nhất.

        NGỮ NGHĨA LUỒNG: xử lý theo lô KHÔNG phá vỡ tính đúng đắn của Flajolet-Martin
        vì trạng thái chỉ là R_j = max, mà max có tính kết hợp và lũy đẳng — kết quả
        không phụ thuộc thứ tự hay cách nhóm. Miễn là truy vấn xảy ra ở biên lô,
        đây là vi-lô (micro-batch) hợp lệ, đúng cách các hệ thống luồng thật vận hành.
        Với DGIM thì KHÔNG được làm vậy, vì trạng thái phụ thuộc thứ tự và timestamp.
        """
        import numpy as np

        arr = np.ascontiguousarray(items, dtype=np.uint64)
        if arr.size == 0:
            return
        self._n_updates += int(arr.size)

        seeds = np.asarray(self._seeds, dtype=np.uint64)
        c1 = np.uint64(0x9E3779B97F4A7C15)
        c2 = np.uint64(0xBF58476D1CE4E5B9)
        c3 = np.uint64(0x94D049BB133111EB)
        s30, s27, s31 = np.uint64(30), np.uint64(27), np.uint64(31)
        one = np.uint64(1)

        best = np.asarray(self.R, dtype=np.uint8)
        for start in range(0, arr.size, chunk):
            block = arr[start:start + chunk]
            # (len(block), m) — số học uint64 của numpy cuộn vòng mod 2^64,
            # đúng ngữ nghĩa mà SplitMix64 yêu cầu.
            z = block[:, None] ^ seeds[None, :]
            z = z + c1
            z = (z ^ (z >> s30)) * c2
            z = (z ^ (z >> s27)) * c3
            z = z ^ (z >> s31)
            # Số số 0 ở cuối = popcount((z & -z) - 1). Với z = 0, (0-1) cuộn thành
            # toàn bit 1 -> 64, khớp quy ước của _trailing_zeros.
            lowbit = z & (~z + one)
            r = np.bitwise_count(lowbit - one).astype(np.uint8)
            np.maximum(best, r.max(axis=0), out=best)

        self.R = best.tolist()

    # -- Các chiến lược tổng hợp (slide tr.40) -----------------------------

    def estimate_single(self) -> float:
        """Ước lượng từ MỘT hàm băm — 2^R. Phương sai rất lớn."""
        return float(2 ** self.R[0])

    def estimate_mean(self) -> float:
        """Trung bình các 2^R_j — nhạy với ngoại lệ."""
        return statistics.fmean(2.0 ** r for r in self.R)

    def estimate_median(self) -> float:
        """Trung vị các 2^R_j — ổn định hơn nhưng LUÔN là lũy thừa của 2."""
        return float(statistics.median(2.0 ** r for r in self.R))

    def estimate(self, corrected: bool = False) -> float:
        """Chiến lược khuyến nghị của slide tr.40: trung vị của các trung bình nhóm.

        Phép lấy trung bình trong nhóm phá vỡ ràng buộc "luôn là lũy thừa của 2"
        vốn giới hạn độ chính xác của ước lượng bằng trung vị thuần.
        """
        per_group = self.m // self.g
        means = [
            statistics.fmean(2.0 ** r for r in self.R[i * per_group:(i + 1) * per_group])
            for i in range(self.g)
        ]
        est = float(statistics.median(means))
        return est / CALIBRATION["median_of_means"] if corrected else est

    def estimate_loglog(self, corrected: bool = True) -> float:
        """Mũ hóa SAU khi lấy trung bình R — mở rộng ngoài slide.

        Slide tr.40 nêu ba chiến lược, cả ba đều tổng hợp các giá trị 2^R_j đã mũ
        hóa. Vì 2^R tăng theo cấp số nhân, một hàm băm gặp may với R lớn hơn 3 đơn
        vị sẽ kéo trung bình lên gấp 8 lần — đúng vấn đề "bị ảnh hưởng bởi outlier"
        mà slide cảnh báo.

        Lấy trung bình R_j TRƯỚC rồi mới mũ hóa loại bỏ hiệu ứng đó, vì R chỉ tăng
        theo logarit. Đây là ý tưởng nền của LogLog (Durand & Flajolet, 2003), hậu
        duệ trực tiếp của Flajolet-Martin.

        Đưa vào để thực nghiệm E5 có thể trả lời câu hỏi: sơ đồ của slide đã đủ
        chưa, hay cần đi xa hơn để đạt độ chính xác mong muốn?

        Đây là chiến lược có bội số chệch ỔN ĐỊNH NHẤT (±2%), nên sau hiệu chuẩn
        nó cũng là chiến lược chính xác nhất. Là ước lượng khuyến nghị cho CityFlow.
        """
        est = 2.0 ** statistics.fmean(self.R)
        if not corrected:
            return est
        return est / ALPHA_M_LOGLOG.get(self.m, DEFAULT_ALPHA_LOGLOG)

    def all_estimates(self) -> dict[str, float]:
        """Toàn bộ chiến lược, cả dạng thô lẫn dạng đã hiệu chuẩn (cho E5)."""
        return {
            "single": self.estimate_single(),
            "mean_raw": self.estimate_mean(),
            "mean_cal": self.estimate_mean() / CALIBRATION["mean"],
            "median_raw": self.estimate_median(),
            "median_cal": self.estimate_median() / CALIBRATION["median"],
            "median_of_means_raw": self.estimate(),
            "median_of_means_cal": self.estimate(corrected=True),
            "loglog_raw": self.estimate_loglog(corrected=False),
            "loglog_cal": self.estimate_loglog(),
            "median_of_means_phi": self.estimate() / PHI_LITERATURE,
        }

    # -- Nội quan ----------------------------------------------------------

    def memory_bytes(self) -> int:
        return (sys.getsizeof(self.R) + sum(sys.getsizeof(r) for r in self.R)
                + sys.getsizeof(self._seeds) + sum(sys.getsizeof(s) for s in self._seeds))

    def theoretical_bits(self) -> float:
        """O(m · log N) bit: mỗi hàm băm chỉ cần lưu R, tối đa 6 bit cho R <= 63."""
        return self.m * 6.0

    def __repr__(self) -> str:
        return f"FlajoletMartin(m={self.m}, g={self.g}, est={self.estimate():,.0f})"
