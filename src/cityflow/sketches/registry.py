"""SketchRegistry — quản lý 535 luồng sketch song song với một đồng hồ chung.

Đây là hiện thực hóa trực tiếp tình huống slide chương Data Streaming tr.53:

    "N có thể rất lớn (hàng triệu phần tử). Có thể có nhiều luồng đồng thời —
     KHÔNG THỂ GIỮ NHIỀU CỬA SỔ."

---------------------------------------------------------------------------
TỐI ƯU HÓA THEN CHỐT — vì sao không lặp qua 535 luồng mỗi sự kiện
---------------------------------------------------------------------------

Cách ngây thơ: mỗi sự kiện, gọi update(bit) cho cả 535 luồng, trong đó 533 luồng
nhận bit 0. Với 19,7 triệu sự kiện là 10,5 TỶ lời gọi hàm — bất khả thi trong Python.

Cách ở đây dựa trên hai quan sát:

  1. Slide tr.62: "Nếu bit = 0 — không cần thay đổi gì". Luồng nhận bit 0 không
     đổi trạng thái, nên KHÔNG cần gọi gì cả.

  2. Thứ duy nhất mọi luồng cùng cần là ĐỒNG HỒ. Thay vì để mỗi luồng tự đếm,
     dùng một đồng hồ toàn cục và truyền vào lúc ghi/truy vấn.

Hệ quả: mỗi sự kiện chỉ chạm ~2-15 luồng thực sự nhận bit 1. Việc loại bucket hết
hạn được hoãn tới lúc TRUY VẤN (lazy expiration) — luồng không ai hỏi thì không
tốn công dọn dẹp.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import AIRPORT_ZONES, N_ZONES
from .ams import AMS
from .dgim import DGIM
from .dgim_integer import DGIMInteger
from .flajolet_martin import FlajoletMartin
from .reservoir import ReservoirSampler

# Vị từ luồng toàn cục. "Thanh toán tiền mặt" của Phase 4 đã bị loại vì FHVHV
# không có cột payment_type (Uber/Lyft không thu tiền mặt) — thay bằng "giá cao".
# Xem docs/04_DATA_UNDERSTANDING §6.
PREDICATE_STREAMS = ["is_airport", "is_long_trip", "has_congestion",
                     "is_shared", "is_high_fare"]


@dataclass(slots=True)
class RegistryConfig:
    """Tham số đã chốt qua thực nghiệm E1-E6."""

    N: int = 1_000_000
    dgim_r: int = 8
    """E2: r=8 cho sai số 2,43% với bộ nhớ gần như không đổi so với r=2."""

    revenue_m: int = 8
    revenue_r_alloc: tuple[int, ...] = (3, 5, 7, 10, 13, 12, 9, 5)
    """E4: phân bổ sqrt_weighted ngân sách 64 — sai số 0,907%."""

    fm_m: int = 256
    fm_g: int = 1
    """E5: m=256 cho sai số 6,4%, p90 10,6% — dưới cận 11,2% của 2^R đơn."""

    ams_k: int = 100
    """E6: k=100 cho sai số 7,1%."""

    reservoir_s: int = 100_000


@dataclass
class SketchRegistry:
    """Toàn bộ trạng thái sketch của CityFlow."""

    cfg: RegistryConfig = field(default_factory=RegistryConfig)
    now: int = 0

    pu_streams: dict[int, DGIM] = field(default_factory=dict)
    do_streams: dict[int, DGIM] = field(default_factory=dict)
    predicate_streams: dict[str, DGIM] = field(default_factory=dict)
    revenue: DGIMInteger = None  # type: ignore[assignment]
    routes: FlajoletMartin = None  # type: ignore[assignment]
    zone_moment: AMS = None  # type: ignore[assignment]
    sample: ReservoirSampler = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        c = self.cfg
        # Tạo sẵn đủ 265 luồng cho mỗi hướng. 3/265 khu vực không bao giờ là điểm
        # đón (docs/04 §2.3) — chúng vẫn phải tồn tại và trả 0 khi truy vấn.
        self.pu_streams = {z: DGIM(c.N, c.dgim_r) for z in range(1, N_ZONES + 1)}
        self.do_streams = {z: DGIM(c.N, c.dgim_r) for z in range(1, N_ZONES + 1)}
        self.predicate_streams = {p: DGIM(c.N, c.dgim_r) for p in PREDICATE_STREAMS}
        self.revenue = DGIMInteger(c.N, m=c.revenue_m, r_alloc=list(c.revenue_r_alloc))
        self.routes = FlajoletMartin(m=c.fm_m, g=c.fm_g)
        self.zone_moment = AMS(k=c.ams_k)
        self.sample = ReservoirSampler(s=c.reservoir_s)

    @property
    def n_streams(self) -> int:
        return len(self.pu_streams) + len(self.do_streams) + len(self.predicate_streams)

    # -- Nạp sự kiện -------------------------------------------------------

    def update(self, pu: int, do: int, revenue_int: int, predicates: dict[str, bool],
               record=None) -> None:
        """Nạp một sự kiện chuyến đi.

        Chỉ chạm vào các luồng thực sự nhận bit 1 — xem docstring của module.
        """
        self.now += 1
        t = self.now

        self.pu_streams[pu].record(t)
        self.do_streams[do].record(t)

        for name, is_true in predicates.items():
            if is_true:
                self.predicate_streams[name].record(t)

        if revenue_int:
            self.revenue.record(t, revenue_int)

        self.routes.update(pu * 1000 + do)
        self.zone_moment.update(pu)
        self.sample.update(record if record is not None else (pu, do))

    def update_batch(self, pu, do, revenue_int, predicate_arrays: dict[str, object]) -> None:
        """Nạp một lô sự kiện — đường đi hiệu năng cao.

        Thực nghiệm E7 chỉ ra Flajolet-Martin chiếm 97,2% thời gian vì nó chạy m=256
        phép băm cho MỖI sự kiện trong vòng lặp Python. Ở đây gom cả lô vào một lời
        gọi update_many đã vector hóa.

        Ranh giới ngữ nghĩa:
          - Flajolet-Martin XỬ LÝ THEO LÔ ĐƯỢC vì trạng thái là max, có tính kết hợp
            và lũy đẳng — không phụ thuộc thứ tự.
          - DGIM, AMS, Reservoir PHẢI xử lý tuần tự vì trạng thái phụ thuộc thứ tự
            và timestamp. Chúng vẫn chạy trong vòng lặp, nhưng chi phí không đáng kể
            (đo được: toàn bộ 535 luồng DGIM chỉ chiếm ~1,5% thời gian).

        Truy vấn chỉ hợp lệ ở biên lô — đúng mô hình vi-lô (micro-batch) mà các hệ
        thống xử lý luồng thực tế sử dụng.
        """
        import numpy as np

        n = len(pu)
        t0 = self.now
        pu_l = pu.tolist() if hasattr(pu, "tolist") else list(pu)
        do_l = do.tolist() if hasattr(do, "tolist") else list(do)
        rev_l = revenue_int.tolist() if hasattr(revenue_int, "tolist") else list(revenue_int)
        pred_l = {k: (v.tolist() if hasattr(v, "tolist") else list(v))
                  for k, v in predicate_arrays.items()}

        pu_s, do_s, pred_s = self.pu_streams, self.do_streams, self.predicate_streams
        rev_sketch, ams, res = self.revenue, self.zone_moment, self.sample

        for i in range(n):
            t = t0 + i + 1
            p, d = pu_l[i], do_l[i]
            pu_s[p].record(t)
            do_s[d].record(t)
            for name, arr in pred_l.items():
                if arr[i]:
                    pred_s[name].record(t)
            v = rev_l[i]
            if v:
                rev_sketch.record(t, v)
            ams.update(p)
            res.update((p, d))

        # Đường đi vector hóa cho Flajolet-Martin.
        route = (np.asarray(pu_l, dtype=np.int64) * 1000
                 + np.asarray(do_l, dtype=np.int64))
        self.routes.update_many(route)

        self.now = t0 + n

    # -- Truy vấn ----------------------------------------------------------

    def count_pickups(self, zone: int, k: int | None = None) -> int:
        """Q1 — số chuyến đón từ `zone` trong k sự kiện gần nhất."""
        return self.pu_streams[zone].query(k, self.now)

    def count_dropoffs(self, zone: int, k: int | None = None) -> int:
        return self.do_streams[zone].query(k, self.now)

    def count_predicate(self, name: str, k: int | None = None) -> int:
        return self.predicate_streams[name].query(k, self.now)

    def total_revenue(self, k: int | None = None) -> int:
        """Q2 — tổng doanh thu ước lượng trong k sự kiện gần nhất."""
        return self.revenue.query(k, self.now)

    def distinct_routes(self) -> float:
        """Q3 — số tuyến phân biệt."""
        return self.routes.estimate_loglog()

    def surprise_number(self) -> float:
        """Q4 — mô-men bậc 2 của phân phối khu vực đón."""
        return self.zone_moment.surprise_number()

    def heatmap(self, k: int | None = None) -> dict[int, int]:
        """Ước lượng cho TOÀN BỘ 265 khu vực — nguồn dữ liệu của bản đồ nhiệt."""
        return {z: s.query(k, self.now) for z, s in self.pu_streams.items()}

    def airport_share(self, k: int | None = None) -> float:
        """Tỷ lệ chuyến liên quan sân bay — ví dụ truy vấn tổ hợp."""
        total = sum(self.pu_streams[z].query(k, self.now) for z in range(1, N_ZONES + 1))
        if total == 0:
            return 0.0
        return self.count_predicate("is_airport", k) / total

    # -- Nội quan ----------------------------------------------------------

    def memory_bytes(self) -> dict[str, int]:
        """Bộ nhớ theo từng nhóm — nguyên tắc P2, đo thật chứ không ước lượng."""
        pu = sum(s.memory_bytes() for s in self.pu_streams.values())
        do = sum(s.memory_bytes() for s in self.do_streams.values())
        pred = sum(s.memory_bytes() for s in self.predicate_streams.values())
        detail = {
            "pu_zones": pu, "do_zones": do, "predicates": pred,
            "revenue": self.revenue.memory_bytes(),
            "routes": self.routes.memory_bytes(),
            "ams": self.zone_moment.memory_bytes(),
            "reservoir": self.sample.memory_bytes(),
        }
        detail["total"] = sum(detail.values())
        detail["total_without_reservoir"] = detail["total"] - detail["reservoir"]
        return detail

    def total_buckets(self) -> int:
        return (sum(s.n_buckets() for s in self.pu_streams.values())
                + sum(s.n_buckets() for s in self.do_streams.values())
                + sum(s.n_buckets() for s in self.predicate_streams.values())
                + sum(s.n_buckets() for s in self.revenue.streams))

    def __repr__(self) -> str:
        return (f"SketchRegistry(streams={self.n_streams}, now={self.now:,}, "
                f"buckets={self.total_buckets():,})")


AIRPORT_ZONE_SET = frozenset(AIRPORT_ZONES)
