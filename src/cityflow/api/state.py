"""Trạng thái dùng chung của ứng dụng API.

Registry sống trong bộ nhớ tiến trình API (đúng bản chất sketch luồng — không có
"lưu trữ" trung gian). Việc nạp dữ liệu chạy nền để không chặn vòng lặp sự kiện.
"""

from __future__ import annotations

import asyncio
import csv
import time
from dataclasses import dataclass, field

import numpy as np

from ..config import PROCESSED_DIR, REFERENCE_DIR
from ..ingest.replay import PREDICATE_COLUMNS, load_events
from ..sketches.registry import SketchRegistry


@dataclass
class LoadStatus:
    ready: bool = False
    loading: bool = False
    n_loaded: int = 0
    n_total: int = 0
    started_at: float | None = None
    elapsed_s: float = 0.0
    error: str | None = None

    @property
    def progress(self) -> float:
        return self.n_loaded / self.n_total if self.n_total else 0.0

    @property
    def throughput(self) -> float:
        return self.n_loaded / self.elapsed_s if self.elapsed_s > 0 else 0.0


@dataclass
class MiningCache:
    """Kết quả FP-Growth + luật, tính một lần khi khởi động (tĩnh cho cả tháng).

    Không tính lại theo từng sự kiện — tầng khai phá mẫu hoạt động trên toàn bộ
    lịch sử tháng đã sắp xếp (đúng thiết kế basket_builder), không phải trên
    trạng thái sketch đang chạy.
    """

    ready: bool = False
    percentile: float = 90.0
    min_support: int = 148
    n_baskets: int = 0
    rules: list = field(default_factory=list)  # list[Rule]


@dataclass
class AppState:
    registry: SketchRegistry = field(default_factory=SketchRegistry)
    status: LoadStatus = field(default_factory=LoadStatus)
    mining: MiningCache = field(default_factory=MiningCache)
    zone_names: dict[int, str] = field(default_factory=dict)
    zone_boroughs: dict[int, str] = field(default_factory=dict)
    month: str = "2024-01"
    replay_speed: float = 0.0
    """Sự kiện/giây khi phát lại sau khi bắt kịp dữ liệu. 0 = chạy hết tốc lực,
    không throttle (mặc định — bắt kịp càng nhanh càng tốt cho môi trường demo)."""

    def load_zone_names(self) -> None:
        path = REFERENCE_DIR / "taxi_zone_lookup.csv"
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                zid = int(row["LocationID"])
                self.zone_names[zid] = row["Zone"]
                self.zone_boroughs[zid] = row["Borough"]


state = AppState()


async def run_ingest(batch_size: int = 65_536) -> None:
    """Nạp toàn bộ tháng dữ liệu vào registry, chạy trong luồng nền.

    update_batch() là hàm CPU-bound đồng bộ; chạy qua run_in_executor để không
    chặn vòng lặp sự kiện asyncio — các endpoint khác vẫn trả lời được trong lúc nạp.
    """
    state.status.loading = True
    state.status.started_at = time.perf_counter()

    try:
        events = await asyncio.get_event_loop().run_in_executor(
            None, load_events, state.month, None
        )
        state.status.n_total = events.n
        loop = asyncio.get_event_loop()

        for start in range(0, events.n, batch_size):
            stop = min(start + batch_size, events.n)
            preds = {name: events.predicates[name][start:stop] for name in PREDICATE_COLUMNS}

            await loop.run_in_executor(
                None, state.registry.update_batch,
                events.pu_zone[start:stop], events.do_zone[start:stop],
                events.revenue_int[start:stop], preds,
            )
            state.status.n_loaded = stop
            state.status.elapsed_s = time.perf_counter() - state.status.started_at

            if state.replay_speed > 0:
                # Throttle để mô phỏng phát lại thời gian thực cho mục đích trình bày.
                target_elapsed = stop / state.replay_speed
                sleep_for = target_elapsed - state.status.elapsed_s
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)

        state.status.ready = True
    except Exception as e:  # noqa: BLE001
        state.status.error = f"{type(e).__name__}: {e}"
        raise
    finally:
        state.status.loading = False


async def run_mining() -> None:
    """Xây giỏ hàng + khai phá luật một lần khi khởi động (Q6, tầng bắt buộc).

    Chạy song song với run_ingest() — không phụ thuộc lẫn nhau vì mining đọc
    thẳng file parquet đã xử lý, không đọc từ registry đang chạy.

    Cấu hình đã chốt qua thực nghiệm (docs/09_KET_QUA_MINING.md §1): phân vị 90%
    thay vì 80% mặc định của Phase 4 — ở 80% giỏ hàng quá dày (TB 44/257 item),
    FP-Growth không hội tụ ở min_sup thấp.
    """
    import pyarrow.parquet as pq

    from ..config import PROCESSED_DIR
    from ..mining.basket_builder import build_baskets
    from ..mining.fpgrowth import fpgrowth
    from ..mining.rules import generate_rules

    try:
        path = PROCESSED_DIR / f"events_{state.month}.parquet"
        table = await asyncio.get_event_loop().run_in_executor(
            None, lambda: pq.read_table(path, columns=["pickup_datetime", "pu_zone"])
        )
        ts = table["pickup_datetime"].to_numpy(zero_copy_only=False).astype("datetime64[s]")
        pu = table["pu_zone"].to_numpy(zero_copy_only=False).astype(np.int64)

        bs = await asyncio.get_event_loop().run_in_executor(
            None, build_baskets, ts, pu, 265, 15, state.mining.percentile
        )
        n_txn = bs.n_baskets
        # min_sup=7% (không phải 5% như E9 khai phá mẫu sâu nhất): ở 5% có mẫu dài
        # tới 11 item, và generate_rules() sinh MỌI cách tách tiền đề/hệ quả — đo
        # được > 1 TRIỆU luật, không phù hợp phục vụ trực tiếp qua API. Cấu hình
        # 7% đã kiểm chứng cho 484 luật trong docs/09_KET_QUA_MINING.md.
        min_sup = max(2, int(0.07 * n_txn))

        freq = await asyncio.get_event_loop().run_in_executor(
            None, fpgrowth, bs.baskets, min_sup
        )
        rules = await asyncio.get_event_loop().run_in_executor(
            None, generate_rules, freq, n_txn, 0.5, 3  # max_antecedent_size=3: chặn bùng nổ
        )

        state.mining.n_baskets = n_txn
        state.mining.min_support = min_sup
        state.mining.rules = rules
        state.mining.ready = True
    except FileNotFoundError:
        pass  # dữ liệu chưa được chuẩn bị — /api/rules trả danh sách rỗng
