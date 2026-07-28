from __future__ import annotations

from fastapi import APIRouter

from ..state import state

router = APIRouter()


@router.get("/status")
def get_status() -> dict:
    """Tiến độ nạp dữ liệu — dashboard poll endpoint này khi khởi động."""
    s = state.status
    return {
        "ready": s.ready, "loading": s.loading, "error": s.error,
        "n_loaded": s.n_loaded, "n_total": s.n_total, "progress": s.progress,
        "elapsed_s": round(s.elapsed_s, 1), "throughput": round(s.throughput, 0),
        "now": state.registry.now,
        "n_streams": state.registry.n_streams,
    }
