"""REQ-1 验收：投递文本 → 归一化 → 入库 → 可读回。

用 SQLite 内存库，**不依赖 PostgreSQL / Docker**，随时可跑。
"""
import os

# 在导入 app 前，把 DATABASE_URL 指到 sqlite，避免 lifespan 的 init_db 去连真实 PG（会快速失败、被跳过）
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base, get_db
from backend.app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_simulate_and_readback(client):
    """投递一条文本 → 返回 id → 读回，字段齐全。"""
    r = client.post(
        "/api/v1/messages/simulate",
        json={
            "external_group_id": "sim_group_001",
            "sender_external_id": "cust_laozhou",
            "content_type": "text",
            "content_text": "5050灯带和2835防水等级有啥区别，能做IP67吗？",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    conv_id = body["data"]["conversation_id"]
    assert body["data"]["message_id"]

    r2 = client.get(f"/api/v1/conversations/{conv_id}")
    assert r2.status_code == 200
    conv = r2.json()["data"]
    assert conv["external_group_id"] == "sim_group_001"
    assert len(conv["messages"]) == 1
    m = conv["messages"][0]
    assert m["direction"] == "inbound"
    assert m["channel"] == "simulator"
    assert m["content_type"] == "text"
    assert "IP67" in m["content_text"]


def test_two_messages_same_group_one_conversation(client):
    """同群多条消息 → 同一个会话。"""
    g = "sim_group_001"
    for i in range(2):
        client.post(
            "/api/v1/messages/simulate",
            json={
                "external_group_id": g,
                "sender_external_id": "cust_laozhou",
                "content_text": f"第{i + 1}条",
            },
        )
    convs = client.get("/api/v1/conversations").json()["data"]
    assert len(convs) == 1
    conv = client.get(f"/api/v1/conversations/{convs[0]['id']}").json()["data"]
    assert len(conv["messages"]) == 2


def test_non_text_normalizes(client):
    """非文字消息：content_text 空、content_type=voice（为 REQ-12 预留接口）。"""
    r = client.post(
        "/api/v1/messages/simulate",
        json={
            "external_group_id": "sim_group_002",
            "sender_external_id": "cust_lin",
            "content_type": "voice",
            "content_text": None,
        },
    )
    assert r.status_code == 200
    conv_id = r.json()["data"]["conversation_id"]
    m = client.get(f"/api/v1/conversations/{conv_id}").json()["data"]["messages"][0]
    assert m["content_type"] == "voice"
    assert m["content_text"] is None
