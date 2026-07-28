-- CityFlow — lược đồ PostgreSQL
-- Theo thiết kế Phase 4 §6.2, điều chỉnh theo dữ liệu thật đã xác minh ở Phase 5.

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- cho gen_random_uuid()

-- ============================================================================
-- Danh mục khu vực — 265 khu vực taxi NYC TLC (đã xác minh docs/04 §2.3)
-- ============================================================================
CREATE TABLE zones (
    location_id   SMALLINT PRIMARY KEY,       -- 1..265
    borough       TEXT NOT NULL,
    zone_name     TEXT NOT NULL,
    service_zone  TEXT,
    is_airport    BOOLEAN NOT NULL DEFAULT FALSE,  -- {1, 132, 138}
    geometry      JSONB                        -- GeoJSON polygon (taxi_zones.geojson)
);

-- ============================================================================
-- Ảnh chụp sketch định kỳ — cho phép API trả lời không cần giữ tiến trình sống
-- ============================================================================
CREATE TABLE sketch_snapshots (
    id            BIGSERIAL PRIMARY KEY,
    stream_key    TEXT NOT NULL,               -- 'pu_zone_161', 'revenue', 'routes_fm', ...
    sketch_type   TEXT NOT NULL,                -- 'dgim' | 'dgim_int' | 'fm' | 'ams' | 'reservoir'
    event_seq     BIGINT NOT NULL,              -- vị trí trong luồng (đồng hồ toàn cục)
    state         JSONB NOT NULL,               -- bucket / R / biến AMS, tùy sketch_type
    memory_bytes  INTEGER NOT NULL,             -- đo thật bằng memory_bytes(), nguyên tắc P2
    captured_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_snapshots_stream_seq ON sketch_snapshots (stream_key, event_seq DESC);

-- ============================================================================
-- Tổng hợp cửa sổ 15 phút — đầu vào tầng khai phá mẫu (Q6)
-- ============================================================================
CREATE TABLE window_aggregates (
    window_start   TIMESTAMPTZ NOT NULL,
    location_id    SMALLINT NOT NULL REFERENCES zones,
    trip_count     INTEGER NOT NULL,
    percentile_thr NUMERIC(10,2),               -- ngưỡng phân vị của CHÍNH khu vực này
    is_hot         BOOLEAN NOT NULL,             -- count > percentile_thr (rời rạc hóa, docs/09 §1)
    PRIMARY KEY (window_start, location_id)
);
CREATE INDEX idx_window_agg_hot ON window_aggregates (window_start) WHERE is_hot;

-- ============================================================================
-- Tập mục thường xuyên — kết quả FP-Growth (Q6)
-- ============================================================================
CREATE TABLE mining_runs (
    run_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month          TEXT NOT NULL,                -- '2024-01'
    percentile     NUMERIC(5,2) NOT NULL,         -- 90.0 — xem docs/09 §1 lý do đổi từ 80
    min_support    INTEGER NOT NULL,
    n_baskets      INTEGER NOT NULL,
    algorithm      TEXT NOT NULL DEFAULT 'fpgrowth',
    elapsed_ms     DOUBLE PRECISION,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE frequent_itemsets (
    id             BIGSERIAL PRIMARY KEY,
    run_id         UUID NOT NULL REFERENCES mining_runs,
    items          SMALLINT[] NOT NULL,          -- LocationID trong tập mục
    support_count  INTEGER NOT NULL,
    support_rel    REAL NOT NULL,
    is_closed      BOOLEAN NOT NULL DEFAULT FALSE,
    is_maximal     BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_itemsets_run ON frequent_itemsets (run_id);
CREATE INDEX idx_itemsets_items ON frequent_itemsets USING GIN (items);

-- ============================================================================
-- Luật kết hợp — đầy đủ 10 độ đo (docs/09, mining/interestingness.py)
-- ============================================================================
CREATE TABLE association_rules (
    id             BIGSERIAL PRIMARY KEY,
    run_id         UUID NOT NULL REFERENCES mining_runs,
    antecedent     SMALLINT[] NOT NULL,
    consequent     SMALLINT[] NOT NULL,
    sup_a          INTEGER NOT NULL,
    sup_b          INTEGER NOT NULL,
    sup_ab         INTEGER NOT NULL,
    n_transactions INTEGER NOT NULL,
    support        REAL, confidence REAL, lift REAL, chi_square REAL,
    all_confidence REAL, coherence REAL, cosine REAL,
    kulczynski     REAL, max_confidence REAL, imbalance_ratio REAL
);
CREATE INDEX idx_rules_run ON association_rules (run_id);
CREATE INDEX idx_rules_kulc ON association_rules (run_id, kulczynski DESC);
CREATE INDEX idx_rules_lift ON association_rules (run_id, lift DESC);

-- ============================================================================
-- Kết quả benchmark — E1..E12 (docs/05-09)
-- ============================================================================
CREATE TABLE benchmark_results (
    id             BIGSERIAL PRIMARY KEY,
    experiment     TEXT NOT NULL,                -- 'E1'..'E12'
    params         JSONB NOT NULL,                -- {N, r, m, g, k, min_sup, ...}
    exact_value    DOUBLE PRECISION,
    estimated      DOUBLE PRECISION,
    rel_error      DOUBLE PRECISION,
    theoretical_bound DOUBLE PRECISION,
    memory_bytes   BIGINT,
    elapsed_ms     DOUBLE PRECISION,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_bench_experiment ON benchmark_results (experiment, created_at DESC);

-- ============================================================================
-- Dữ liệu khởi tạo: nạp danh mục khu vực từ CSV khi container lên
-- (thực hiện bằng script Python riêng do cần parse CSV UTF-8 có dấu tiếng Anh;
--  bảng zones được nạp qua scripts/08_load_zones.py, không nạp bằng SQL thuần)
