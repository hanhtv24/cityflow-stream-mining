"""Cấu hình tập trung.

Nguyên tắc P5 (Phase 4): mọi tham số thuật toán đều cấu hình được, không hard-code,
vì chúng là biến độc lập của ma trận thực nghiệm E1–E12.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# --- Đường dẫn ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dữ liệu thô nằm NGOÀI OneDrive: hàng trăm MB parquet không nên được đồng bộ.
DATA_DIR = Path(os.environ.get("CITYFLOW_DATA_DIR", r"C:\Users\leotran\cityflow_data"))
RAW_DIR = DATA_DIR / "raw"
REFERENCE_DIR = DATA_DIR / "reference"
PROCESSED_DIR = DATA_DIR / "processed"

DOCS_DIR = PROJECT_ROOT / "docs"
FIGURES_DIR = DOCS_DIR / "figures"


# --- Tham số thuật toán ---------------------------------------------------


@dataclass(frozen=True)
class DGIMConfig:
    """Tham số DGIM. Xem slide chương Data Streaming tr.57-65."""

    N: int = 1_000_000
    """Độ rộng cửa sổ trượt (số sự kiện gần nhất)."""

    r: int = 2
    """Số bucket tối đa mỗi kích thước. r=2 là mặc định của slide tr.60.
    Tăng r giảm sai số theo O(1/r) — biến độc lập của thực nghiệm E2."""


@dataclass(frozen=True)
class DGIMIntegerConfig:
    """DGIM mở rộng cho tổng số nguyên. Slide tr.66."""

    N: int = 1_000_000
    m: int = 8
    """Số bit biểu diễn mỗi giá trị (đơn vị USD, làm tròn).

    ĐÃ XÁC MINH trên FHVHV 2024-01 (19.66M bản ghi):
        p50 = 18.76 | p95 = 68.52 | p99 = 123.87 | p99.9 = 227.42 | max = 1961.28
    -> m=8  phủ 0..255 USD  (kẹp trần ~0.1% chuyến)
    -> m=11 phủ 0..2047 USD (không kẹp)
    Giả định ban đầu m=12 ở Phase 4 là quá rộng. m là biến độc lập của E4."""

    clip_value: int = 255
    """Giá trị kẹp trần tương ứng m=8. Tỷ lệ bị kẹp phải được ghi nhận trong báo cáo."""

    r_allocation: tuple[int, ...] | None = None
    """Phân bổ r theo từng vị trí bit. None = đồng đều r=2 cho mọi bit.
    Giả thuyết H1 (thực nghiệm E4): phân bổ không đồng đều — tăng r cho bit cao —
    cho sai số thấp hơn ở cùng ngân sách bộ nhớ."""


@dataclass(frozen=True)
class FlajoletMartinConfig:
    """Slide tr.37-41."""

    m: int = 64
    """Số hàm băm."""

    g: int = 8
    """Số nhóm. Chiến lược tổng hợp: trung bình trong nhóm -> trung vị các trung bình
    ("Tốt nhất: kết hợp cả hai", slide tr.40)."""

    seed: int = 42


@dataclass(frozen=True)
class AMSConfig:
    """Slide tr.46-51."""

    k: int = 100
    """Số biến ngẫu nhiên X. Ước lượng cải thiện bằng trung bình (slide tr.47)."""

    seed: int = 42


@dataclass(frozen=True)
class ReservoirConfig:
    """Slide tr.19-21."""

    s: int = 100_000
    seed: int = 42


@dataclass(frozen=True)
class MiningConfig:
    """Tầng khai phá mẫu — trả lời Q6."""

    window_minutes: int = 15
    """Độ dài cửa sổ tạo giỏ hàng."""

    hot_percentile: float = 80.0
    """Ngưỡng rời rạc hóa 'hot'. QUAN TRỌNG: phân vị tính RIÊNG cho từng khu vực,
    không dùng ngưỡng tuyệt đối — nếu không kết quả sẽ tầm thường
    ('Midtown luôn bận'). Xem Phase 4 §5.1."""

    min_support: float = 0.05
    min_confidence: float = 0.5


@dataclass(frozen=True)
class Settings:
    dgim: DGIMConfig = field(default_factory=DGIMConfig)
    dgim_int: DGIMIntegerConfig = field(default_factory=DGIMIntegerConfig)
    fm: FlajoletMartinConfig = field(default_factory=FlajoletMartinConfig)
    ams: AMSConfig = field(default_factory=AMSConfig)
    reservoir: ReservoirConfig = field(default_factory=ReservoirConfig)
    mining: MiningConfig = field(default_factory=MiningConfig)

    database_url: str = os.environ.get(
        "CITYFLOW_DATABASE_URL",
        # Cổng host 55432, không phải 5432 mặc định của Postgres: máy phát triển
        # đã có một instance Postgres khác chiếm 5432 (xem docker-compose.yml).
        "postgresql+psycopg://cityflow:cityflow@localhost:55432/cityflow",
    )


settings = Settings()


# --- Khu vực đặc biệt -----------------------------------------------------

N_ZONES = 265
"""ĐÃ XÁC MINH: taxi_zone_lookup.csv có đúng 265 khu vực."""

AIRPORT_ZONES = {1, 132, 138}
"""ĐÃ XÁC MINH: Newark/EWR (1), JFK (132), LaGuardia (138).
JFK và LaGuardia là hai khu vực đón lớn nhất toàn thành phố (1.90% và 1.76%)."""

UNKNOWN_ZONES = {264, 265}
"""ĐÃ XÁC MINH: Borough 'N/A' (264) và 'Unknown' (265).

Tỷ lệ thực tế trên FHVHV 2024-01:
    PULocationID unknown:    765 chuyến (0.004%) -> bỏ qua được
    DOLocationID unknown: 741,161 chuyến (3.77%) -> KHÔNG bỏ qua được

Quyết định: GIỮ các bản ghi này. Với luồng theo khu vực trả, gộp 264/265 thành
một luồng 'unknown' riêng thay vì loại bỏ — loại bỏ 3.77% sẽ làm lệch ground truth
của mọi ước lượng liên quan tới khu vực trả."""

ZONES_NEVER_PICKUP = 3
"""ĐÃ XÁC MINH: chỉ 262/265 khu vực từng xuất hiện làm điểm đón trong tháng 01/2024.
Registry phải xử lý được luồng không có sự kiện nào (bucket rỗng)."""
