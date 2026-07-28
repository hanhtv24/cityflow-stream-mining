"""CityFlow API — FastAPI.

Mỗi endpoint ước lượng đều trả kèm giá trị lý thuyết/tham số liên quan khi có thể,
biến chính API thành công cụ minh chứng (Phase 4 §7).
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import bench, distinct, heatmap, rules, status, surprise, window, zones
from .state import run_ingest, run_mining, state


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load_zone_names()
    asyncio.create_task(run_ingest())
    asyncio.create_task(run_mining())
    yield


app = FastAPI(
    title="CityFlow API",
    description="Truy vấn cửa sổ trượt và khai phá mẫu đồng ùn tắc trên luồng chuyến đi NYC",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(zones.router, prefix="/api", tags=["zones"])
app.include_router(window.router, prefix="/api", tags=["window"])
app.include_router(distinct.router, prefix="/api", tags=["distinct"])
app.include_router(surprise.router, prefix="/api", tags=["surprise"])
app.include_router(heatmap.router, prefix="/api", tags=["heatmap"])
app.include_router(rules.router, prefix="/api", tags=["rules"])
app.include_router(bench.router, prefix="/api", tags=["bench"])
