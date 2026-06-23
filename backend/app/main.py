"""FastAPI 入口。注册路由 + 启动时建表 + 挂载演示 UI（/ui）。"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import handoffs, knowledge, messages, sla, summaries
from .db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 原型期自动建表；DB 未就绪时只告警、不阻塞启动（测试/无 PG 场景）
    try:
        init_db()
    except Exception as e:  # noqa: BLE001
        print(f"[warn] init_db 跳过（DB 未就绪？）：{e}")
    yield


app = FastAPI(title="Digital Customer Service (Demo)", version="0.1.0", lifespan=lifespan)
app.include_router(messages.router)
app.include_router(knowledge.router)
app.include_router(handoffs.router)
app.include_router(sla.router)
app.include_router(summaries.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# 演示用前端（静态挂载，同源避免 CORS）；frontend/ 定位为「演示辅助 UI」（非 P1 功能前端）
_frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if _frontend_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=str(_frontend_dir), html=True), name="ui")
