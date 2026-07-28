"""Kết nối CSDL — dùng chung cho API và các script nạp dữ liệu."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ..config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine
