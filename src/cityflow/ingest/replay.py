"""Tầng L0 — nạp và phát lại luồng sự kiện.

Dữ liệu đầu vào là parquet ĐÃ SẮP THEO pickup_datetime (xem scripts/02_prepare_data.py).
Module này KHÔNG tự sắp xếp — nếu nhận dữ liệu chưa sắp, kết quả sẽ sai.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from ..config import PROCESSED_DIR

# Các cột dùng cho tầng sketch. Giữ hẹp để tiết kiệm bộ nhớ khi nạp 19,7 triệu dòng.
STREAM_COLUMNS = [
    "pu_zone", "do_zone", "revenue_int",
    "is_airport", "is_long_trip", "has_congestion", "is_shared", "is_high_fare",
]

PREDICATE_COLUMNS = ["is_airport", "is_long_trip", "has_congestion", "is_shared", "is_high_fare"]


@dataclass(slots=True)
class EventArrays:
    """Luồng sự kiện dạng mảng cột.

    Mỗi mảng có cùng độ dài n. Chỉ số i là VỊ TRÍ TRONG LUỒNG của sự kiện thứ i,
    cũng chính là đồng hồ toàn cục dùng cho DGIM (đánh số từ 1).
    """

    pu_zone: np.ndarray          # uint16
    do_zone: np.ndarray          # uint16
    revenue_int: np.ndarray      # uint8
    predicates: dict[str, np.ndarray]  # tên -> mảng bool

    @property
    def n(self) -> int:
        return len(self.pu_zone)

    def ones_positions(self, mask: np.ndarray) -> np.ndarray:
        """Vị trí (đồng hồ toàn cục, đánh số từ 1) của các sự kiện thỏa vị từ.

        Đây là đường đi nhanh để nạp DGIM: slide tr.62 nói bit 0 không cần làm gì,
        nên chỉ cần biết vị trí các bit 1. Với 535 luồng, cách này nhanh hơn nhiều
        lần so với lặp qua từng sự kiện rồi gọi update(0) cho 534 luồng.
        """
        return np.flatnonzero(mask) + 1


def load_events(month: str = "2024-01", limit: int | None = None) -> EventArrays:
    """Nạp luồng sự kiện đã chuẩn bị vào bộ nhớ dưới dạng mảng numpy."""
    path = PROCESSED_DIR / f"events_{month}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {path}. Chạy scripts/02_prepare_data.py --month {month} trước."
        )

    table = pq.read_table(path, columns=STREAM_COLUMNS)
    if limit is not None:
        table = table.slice(0, limit)

    return EventArrays(
        pu_zone=table["pu_zone"].to_numpy(zero_copy_only=False).astype(np.uint16),
        do_zone=table["do_zone"].to_numpy(zero_copy_only=False).astype(np.uint16),
        revenue_int=table["revenue_int"].to_numpy(zero_copy_only=False).astype(np.uint8),
        predicates={
            name: table[name].to_numpy(zero_copy_only=False).astype(bool)
            for name in PREDICATE_COLUMNS
        },
    )


def iter_events(path: Path, batch_size: int = 65_536):
    """Phát lại tuần tự từng sự kiện — dùng để đo thông lượng thật (thực nghiệm E7).

    Khác với load_events (nạp cả tháng vào RAM để tính ground truth), hàm này mô phỏng
    đúng ràng buộc luồng: đọc theo lô, xử lý xong là bỏ, không giữ lịch sử.
    """
    reader = pq.ParquetFile(path)
    t = 0
    for batch in reader.iter_batches(batch_size=batch_size, columns=STREAM_COLUMNS):
        cols = {name: batch.column(name).to_numpy(zero_copy_only=False)
                for name in STREAM_COLUMNS}
        for i in range(batch.num_rows):
            t += 1
            yield t, {name: col[i] for name, col in cols.items()}
