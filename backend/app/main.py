"""FastAPI 入口。Sprint-1：注册路由 + 启动时建表。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import handoffs, knowledge, messages
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


@app.get("/health")
def health():
    return {"status": "ok"}
