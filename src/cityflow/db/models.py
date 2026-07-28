"""Mô hình SQLAlchemy — ánh xạ trực tiếp lược đồ sql/init.sql.

Dùng Core (Table) thay vì ORM đầy đủ: khối lượng ghi lớn (frequent_itemsets,
association_rules có thể tới hàng chục nghìn dòng/lần chạy) hưởng lợi từ
executemany của Core hơn là overhead theo dõi đối tượng của ORM.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    ARRAY, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer,
    MetaData, Numeric, REAL, SmallInteger, String, Table, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()

zones = Table(
    "zones", metadata,
    Column("location_id", SmallInteger, primary_key=True),
    Column("borough", String, nullable=False),
    Column("zone_name", String, nullable=False),
    Column("service_zone", String),
    Column("is_airport", Boolean, nullable=False, default=False),
    Column("geometry", JSONB),
)

sketch_snapshots = Table(
    "sketch_snapshots", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("stream_key", String, nullable=False),
    Column("sketch_type", String, nullable=False),
    Column("event_seq", BigInteger, nullable=False),
    Column("state", JSONB, nullable=False),
    Column("memory_bytes", Integer, nullable=False),
    Column("captured_at", DateTime(timezone=True), server_default=func.now()),
)

window_aggregates = Table(
    "window_aggregates", metadata,
    Column("window_start", DateTime(timezone=True), primary_key=True),
    Column("location_id", SmallInteger, ForeignKey("zones.location_id"), primary_key=True),
    Column("trip_count", Integer, nullable=False),
    Column("percentile_thr", Numeric(10, 2)),
    Column("is_hot", Boolean, nullable=False),
)

mining_runs = Table(
    "mining_runs", metadata,
    Column("run_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("month", String, nullable=False),
    Column("percentile", Numeric(5, 2), nullable=False),
    Column("min_support", Integer, nullable=False),
    Column("n_baskets", Integer, nullable=False),
    Column("algorithm", String, nullable=False, default="fpgrowth"),
    Column("elapsed_ms", REAL),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

frequent_itemsets = Table(
    "frequent_itemsets", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), ForeignKey("mining_runs.run_id"), nullable=False),
    Column("items", ARRAY(SmallInteger), nullable=False),
    Column("support_count", Integer, nullable=False),
    Column("support_rel", REAL, nullable=False),
    Column("is_closed", Boolean, nullable=False, default=False),
    Column("is_maximal", Boolean, nullable=False, default=False),
)

association_rules = Table(
    "association_rules", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), ForeignKey("mining_runs.run_id"), nullable=False),
    Column("antecedent", ARRAY(SmallInteger), nullable=False),
    Column("consequent", ARRAY(SmallInteger), nullable=False),
    Column("sup_a", Integer, nullable=False),
    Column("sup_b", Integer, nullable=False),
    Column("sup_ab", Integer, nullable=False),
    Column("n_transactions", Integer, nullable=False),
    Column("support", REAL), Column("confidence", REAL),
    Column("lift", REAL), Column("chi_square", REAL),
    Column("all_confidence", REAL), Column("coherence", REAL), Column("cosine", REAL),
    Column("kulczynski", REAL), Column("max_confidence", REAL), Column("imbalance_ratio", REAL),
)

benchmark_results = Table(
    "benchmark_results", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("experiment", String, nullable=False),
    Column("params", JSONB, nullable=False),
    Column("exact_value", REAL), Column("estimated", REAL), Column("rel_error", REAL),
    Column("theoretical_bound", REAL),
    Column("memory_bytes", BigInteger), Column("elapsed_ms", REAL),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
