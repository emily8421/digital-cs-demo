"""REQ-10/12 单测：转人工暂停 + 非文字如实告知。SQLite + TestClient。

非文字分支（act_on_non_text）不依赖 TEI/pgvector，可在 SQLite 跑；
handed_off 暂停是 handoff_state 字段判定，亦可在 SQLite 跑。
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base, get_db
from backend.app.main import app
from backend.app.models import RoutingRule, Staff


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    s.add(Staff(name="陈总", role="owner", active=True))
    s.add(RoutingRule(scenario="unknown_question", target_role="owner"))
    s.commit()
    s.close()

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _simulate(client, group, content_type="text", text=None):
    body = {
        "external_group_id": group,
        "sender_external_id": "cust",
        "content_type": content_type,
    }
    if text is not None:
        body["content_text"] = text
    return client.post("/api/v1/messages/simulate", json=body)


def test_non_text_tells_and_notifies(client):
    """非文字（voice）→ 如实告知 + 员工提醒，不生成知识作答、不写 gap。"""
    r = _simulate(client, "g1", content_type="voice")
    d = r.json()["data"]
    assert d["hit"] is False
    assert "语音" in d["reply_text"]
    assert "看不了" in d["reply_text"]
    assert d["notification_id"] is not None  # 员工提醒
    assert d["gap_id"] is None  # 非文字不是知识缺口


def test_handoff_state_pauses_orchestration(client):
    """会话置 handed_off 后，新消息不产生自动编排（无 reply/notification）。"""
    cid = _simulate(client, "g1", content_type="voice").json()["data"]["conversation_id"]
    client.post(
        f"/api/v1/conversations/{cid}/handoff-state", json={"handoff_state": "handed_off"}
    )
    # 再投 voice（正常会 act_on_non_text；handed_off 应跳过）
    d = _simulate(client, "g1", content_type="voice").json()["data"]
    assert d["reply_text"] is None  # 暂停：无自动回复
    assert d["notification_id"] is None


def test_handoff_state_resume(client):
    """解除暂停（auto）后恢复自动编排。"""
    cid = _simulate(client, "g1", content_type="voice").json()["data"]["conversation_id"]
    client.post(
        f"/api/v1/conversations/{cid}/handoff-state", json={"handoff_state": "handed_off"}
    )
    assert _simulate(client, "g1", content_type="voice").json()["data"]["reply_text"] is None
    # 解除
    client.post(
        f"/api/v1/conversations/{cid}/handoff-state", json={"handoff_state": "auto"}
    )
    d = _simulate(client, "g1", content_type="voice").json()["data"]
    assert d["reply_text"] is not None
    assert "语音" in d["reply_text"]
