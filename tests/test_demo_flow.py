"""Sprint-7 端到端 Demo 流程集成测试（模拟器通道，串联 P1 全部 REQ）。

monkeypatch 注入 fake 检索（命中/未命中可控），SQLite 内存库跑通 03 §3 Demo 步骤 1-5。
真实串联（TEI+pgvector）见 scripts/demo.py。
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
from backend.app.service.knowledge.search import KnowledgeHit


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    s.add(Staff(name="小雯", role="sales", active=True))
    s.add(Staff(name="陈总", role="owner", active=True))
    s.add(RoutingRule(scenario="presale", target_role="sales"))
    s.add(RoutingRule(scenario="unknown_question", target_role="owner"))
    s.commit()
    s.close()

    # fake 检索：含产品关键词→命中；否则未命中（走缺口）
    def fake_search(db, q, embedder=None):
        if any(k in q for k in ("5050", "2835", "起订", "付款", "防水")):
            return True, [
                KnowledgeHit(
                    id=1,
                    question_pattern="5050/2835",
                    answer="5050亮度高、2835省电，按需选。",
                    score=0.9,
                    status="confirmed",
                )
            ]
        return False, []

    monkeypatch.setattr(
        "backend.app.service.conversation.engine.knowledge_search", fake_search
    )

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


def _sim(client, group, text=None, ctype="text"):
    body = {
        "external_group_id": group,
        "sender_external_id": "cust",
        "content_type": ctype,
    }
    if text is not None:
        body["content_text"] = text
    return client.post("/api/v1/messages/simulate", json=body).json()["data"]


def test_demo_flow_steps_1_to_5(client):
    """03 §3 Demo 步骤 1-5（模拟器通道，企微步骤 6 跳过——Sprint-0 不成立）。"""
    base = "/api/v1"

    # 步骤1：产品参数问题 → 知识作答（REQ-2/3）
    d1 = _sim(client, "g1", "5050和2835灯带区别")
    assert d1["hit"] is True
    assert "5050亮度高" in d1["reply_text"]

    # 步骤2：未覆盖问题 → 请留资 + 缺口转交拍板人（REQ-6）
    d2 = _sim(client, "g2", "你们灯带能用在月球表面吗")
    assert d2["hit"] is False
    assert d2["gap_id"] is not None and d2["handoff_id"] is not None
    assert "留" in d2["reply_text"]  # 请留资口径

    # 步骤3：含手机号满意度留言 → 留资记录（REQ-4/5）
    d3 = _sim(client, "g3", "满意，想订货，电话13912345678")
    assert d3["lead_id"] is not None

    # 步骤4：定时小结 → 经营者收总量+跟进清单+分配对象（REQ-7）
    s4 = client.post(f"{base}/summaries/daily").json()["data"]["summary"]
    assert "条客户消息" in s4 and "需跟进" in s4

    # 步骤5a：语音 → 群内如实告知 + 员工提醒（REQ-12）
    d5 = _sim(client, "g5", ctype="voice")
    assert "语音" in d5["reply_text"]
    assert d5["notification_id"] is not None

    # 步骤5b：标记转人工 → 后续消息不自动回（REQ-10）
    cid5 = d5["conversation_id"]
    client.post(
        f"{base}/conversations/{cid5}/handoff-state", json={"handoff_state": "handed_off"}
    )
    d6 = _sim(client, "g5", "还在吗")
    assert d6["reply_text"] is None  # 暂停：无自动回复
