"""DGIM — đếm bit 1 trong cửa sổ trượt với bộ nhớ O(log^2 N).

Cài đặt from scratch theo slide chương Data Streaming tr.57-65
(Datar, Gionis, Indyk, Motwani).

Bài toán: cho luồng bit vô hạn, trả lời "có bao nhiêu bit 1 trong k bit gần nhất?"
khi không thể lưu k bit.

Ý tưởng: tóm tắt luồng bằng các bucket, mỗi bucket chứa một số bit 1 là LŨY THỪA
CỦA 2 (1, 1, 2, 4, 8, ...). Mỗi bucket chỉ lưu timestamp của bit 1 cuối cùng trong nó.

Bất biến (slide tr.60):
    1. Tối đa r bucket cùng kích thước (mặc định r = 2)
    2. Các bucket không chồng lấn timestamp
    3. Bucket mới nhỏ hơn bucket cũ hơn
    4. Bucket bị loại khi timestamp cuối đã ra khỏi cửa sổ N

Sai số: <= 50% với r = 2, và O(1/r) khi tăng r (slide tr.64).
"""

from __future__ import annotations

import math
import sys
from collections import deque

from .base import Sketch


class DGIM(Sketch):
    """Ước lượng số bit 1 trong cửa sổ trượt N phần tử gần nhất.

    Cấu trúc lưu trữ: ``levels[e]`` là deque các timestamp của những bucket có
    kích thước ``2**e``, sắp theo thứ tự MỚI NHẤT TRƯỚC.

    Cách tổ chức theo tầng này cho phép gộp bucket trong O(1) khấu hao. Cách làm
    ngây thơ — giữ một danh sách phẳng rồi quét tìm bucket cùng cỡ mỗi lần chèn —
    tốn O(số bucket) = O(r·log N) mỗi lần cập nhật, quá chậm cho 19,7 triệu sự kiện.

    Vì mọi bucket ở tầng e+1 đều CŨ HƠN mọi bucket ở tầng e (bất biến 3), bucket
    sinh ra khi gộp hai bucket cũ nhất của tầng e luôn MỚI HƠN mọi bucket đang có
    ở tầng e+1 — nên chỉ cần ``appendleft``, không cần tìm vị trí chèn.
    """

    __slots__ = ("N", "r", "levels", "now", "_ones_seen")

    def __init__(self, N: int, r: int = 2) -> None:
        if N <= 0:
            raise ValueError("N phải dương")
        if r < 2:
            # Slide tr.64 mô tả sơ đồ "duy trì r HOẶC r-1 bucket mỗi kích thước",
            # nên r=1 tương đương "0 hoặc 1 bucket mỗi cỡ" — một cấu hình SUY BIẾN.
            #
            # Vì sao suy biến: khi mỗi cỡ chỉ được giữ một bucket, mọi bucket đều bị
            # gộp ngay khi có bạn cùng cỡ, tạo phản ứng dây chuyền dồn toàn bộ luồng
            # vào MỘT bucket khổng lồ. Bucket gộp kế thừa timestamp của bit 1 gần nhất,
            # nên nó không hết hạn dù chứa các bit 1 đã ra khỏi cửa sổ từ lâu.
            # Đo được: N=2000, mật độ 0.05 -> ước lượng 514 trong khi đáp án đúng là
            # 100 (sai số 414%, vi phạm cận 50%).
            #
            # Với r>=2 luôn tồn tại "bucket em" giữ lại timestamp mới, nên bucket gộp
            # mang timestamp cũ và hết hạn đúng lúc.
            raise ValueError(
                f"r phải >= 2 (nhận r={r}). r=1 làm sơ đồ suy biến: toàn bộ luồng "
                "dồn vào một bucket không bao giờ hết hạn. Xem slide tr.60, tr.64."
            )
        self.N = N
        self.r = r
        self.levels: list[deque[int]] = []
        self.now = 0
        self._ones_seen = 0

    # -- Nạp dữ liệu -------------------------------------------------------

    def update(self, bit: int) -> None:
        """Nạp một bit, tự tăng đồng hồ nội bộ.

        Đây là giao diện đúng như mô tả trong giáo trình, dùng cho unit test tái
        hiện ví dụ trên slide. Trong hệ thống thật, ``SketchRegistry`` dùng
        :meth:`record` với đồng hồ toàn cục dùng chung.
        """
        self.now += 1
        if bit:
            self.record(self.now)

    def record(self, t: int) -> None:
        """Ghi nhận một bit 1 tại vị trí t của đồng hồ toàn cục.

        Bit 0 KHÔNG cần gọi hàm này — slide tr.62: "Nếu bit = 0, không cần thay
        đổi gì". Đây là tối ưu hóa then chốt cho kiến trúc 535 luồng: mỗi sự kiện
        chỉ chạm vào vài luồng nhận bit 1, thay vì lặp qua toàn bộ 535 luồng.
        """
        self.now = t
        self._ones_seen += 1

        if not self.levels:
            self.levels.append(deque())
        self.levels[0].appendleft(t)

        e = 0
        while len(self.levels[e]) > self.r:
            # Gộp HAI BUCKET CŨ NHẤT cùng cỡ (slide tr.62).
            # deque sắp mới-nhất-trước, nên pop() lấy phần tử cũ nhất.
            self.levels[e].pop()                 # bucket cũ nhất — bị nuốt
            merged_ts = self.levels[e].pop()     # bucket cũ thứ hai — giữ timestamp của nó
            # Timestamp của bucket gộp = timestamp của bit 1 GẦN NHẤT trong nó.
            if e + 1 == len(self.levels):
                self.levels.append(deque())
            self.levels[e + 1].appendleft(merged_ts)
            e += 1

    # -- Truy vấn ----------------------------------------------------------

    def expire(self, t_now: int | None = None) -> None:
        """Loại các bucket đã ra khỏi cửa sổ N (bất biến 4).

        Gọi lười (lazy) tại thời điểm truy vấn thay vì mỗi lần cập nhật: với 535
        luồng, dọn dẹp mỗi sự kiện cho mọi luồng sẽ tốn kém vô ích vì phần lớn
        luồng không có sự kiện mới.
        """
        t_now = self.now if t_now is None else t_now
        cutoff = t_now - self.N
        for dq in self.levels:
            while dq and dq[-1] <= cutoff:
                dq.pop()

    def query(self, k: int | None = None, t_now: int | None = None) -> int:
        """Ước lượng số bit 1 trong k phần tử gần nhất (k <= N).

        Quy tắc slide tr.64: cộng kích thước mọi bucket trong cửa sổ, TRỪ ĐI một
        nửa kích thước bucket cũ nhất — vì không biết bao nhiêu phần của bucket
        cũ nhất còn nằm trong cửa sổ.
        """
        t_now = self.now if t_now is None else t_now
        k = self.N if k is None else min(k, self.N)
        self.expire(t_now)

        cutoff = t_now - k
        total = 0
        oldest_ts = None
        oldest_size = 0

        for e, dq in enumerate(self.levels):
            size = 1 << e
            for ts in dq:
                # Chặn trên bằng t_now là phòng vệ: trong vận hành luồng bình thường
                # không thể có bucket ở tương lai. Nhưng nếu ai đó nạp toàn bộ luồng
                # rồi truy vấn tại một mốc quá khứ, thiếu chặn này sẽ cộng cả bucket
                # chưa xảy ra và cho ước lượng lớn hơn sự thật hàng nghìn lần.
                if cutoff < ts <= t_now:
                    total += size
                    if oldest_ts is None or ts < oldest_ts:
                        oldest_ts = ts
                        oldest_size = size

        if oldest_ts is None:
            return 0
        return total - oldest_size // 2

    # -- Nội quan ----------------------------------------------------------

    def bucket_sizes(self) -> list[int]:
        """Kích thước các bucket theo thứ tự mới nhất -> cũ nhất.

        Dùng cho unit test đối chiếu với hình minh họa trên slide.
        """
        pairs = [(ts, 1 << e) for e, dq in enumerate(self.levels) for ts in dq]
        pairs.sort(key=lambda p: -p[0])
        return [size for _, size in pairs]

    def n_buckets(self) -> int:
        return sum(len(dq) for dq in self.levels)

    def exact_ones_seen(self) -> int:
        """Tổng số bit 1 đã từng nạp (mọi thời điểm, không giới hạn cửa sổ).

        Chỉ dùng để kiểm tra tính nhất quán trong test — KHÔNG phải trạng thái
        mà thuật toán DGIM được phép giữ.
        """
        return self._ones_seen

    def memory_bytes(self) -> int:
        total = sys.getsizeof(self.levels)
        for dq in self.levels:
            total += sys.getsizeof(dq)
            total += sum(sys.getsizeof(ts) for ts in dq)
        return total

    def theoretical_bits(self) -> float:
        """Cận lý thuyết O(log^2 N) — slide tr.58-59.

        Mỗi bucket cần:
            - timestamp lưu dạng mod N  -> log2(N) bit
            - kích thước là lũy thừa 2  -> log2(log2(N)) bit
        Số bucket tối đa: r bucket cho mỗi cỡ, có log2(N) cỡ khác nhau.
        """
        log_n = math.log2(self.N)
        bits_per_bucket = log_n + math.log2(max(log_n, 2))
        max_buckets = self.r * log_n
        return bits_per_bucket * max_buckets

    def __repr__(self) -> str:
        return (f"DGIM(N={self.N:,}, r={self.r}, buckets={self.n_buckets()}, "
                f"now={self.now:,}, est={self.query():,})")
