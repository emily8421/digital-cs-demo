"""Sprint-13 P2 端到端集成测试：串联多轮引导 / 身份披露 / 话题级暂停 / 知识回写。

SQLite 内存库 + fake search/embedder（不依赖 TEI/pgvector）。
P1 端到端见 test_demo_flow.py；真实环境（TEI+pgvector）见 demo-script.md。
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

    # fake search：含产品关键词→命中；否则未命中（走缺口）
    def fake_search(db, q, embedder=None):
        if any(k in q for k in ("5050", "2835", "IP67", "防水")):
            return True, [
                KnowledgeHit(
                    id=1,
                    question_pattern="x",
                    answer="产品参数答案",
                    score=0.9,
                    status="confirmed",
                )
            ]
        return False, []

    monkeypatch.setattr("backend.app.service.conversation.engine.knowledge_search", fake_search)
    # fake embedder（知识回写 answer_gap 用）
    monkeypatch.setattr(
        "backend.app.service.knowledge.writeback.default_embed", lambda text: [0.1] * 8
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


def _sim(client, group, sender, text=None, ctype="text"):
    body = {
        "external_group_id": group,
        "sender_external_id": sender,
        "content_type": ctype,
    }
    if text is not None:
        body["content_text"] = text
    return client.post("/api/v1/messages/simulate", json=body).json()["data"]


def test_p2_multiturn_inquiry(client):
    """多轮引导：定制询盘 → 拆项逐条确认 → 摘要转交。"""
    d1 = _sim(client, "g1", "c1", "我要定制灯带")
    assert "颜色" in d1["reply_text"]  # 首轮问颜色
    d2 = _sim(client, "g1", "c1", "蓝色")
    assert "数量" in d2["reply_text"]
    _sim(client, "g1", "c1", "100米")
    _sim(client, "g1", "c1", "要logo")
    d5 = _sim(client, "g1", "c1", "7天")
    assert d5["handoff_id"] is not None  # 收集完转交
    assert "核价" in d5["reply_text"]


def test_p2_identity_disclosure(client):
    """身份披露：被问机器人 → 既定话术承认身份。"""
    d = _sim(client, "g2", "c1", "你是机器人吗")
    assert "小辰" in d["reply_text"] and "AI" in d["reply_text"]


def test_p2_topic_level_handoff(client):
    """话题级暂停：cust_A 暂停 → cust_A 无回复、cust_B 正常。"""
    d1 = _sim(client, "g3", "cust_A", "5050和2835区别")  # cust_A 造会话 + 作答
    cid = d1["conversation_id"]
    client.post(
        f"/api/v1/conversations/{cid}/topic-handoff",
        json={"topic_key": "cust_A", "handoff_state": "handed_off"},
    )
    d2 = _sim(client, "g3", "cust_A", "能做IP67吗")
    assert d2["reply_text"] is None  # cust_A 话题暂停
    d3 = _sim(client, "g3", "cust_B", "能做IP67吗")
    assert d3["reply_text"] is not None  # cust_B 其他话题正常作答


def test_p2_knowledge_writeback(client):
    """知识回写：缺口 → 补答(pending) → 确认(confirmed)。"""
    g = _sim(client, "g4", "c1", "任意未命中问题xyz")  # 未命中 → gap
    assert g["gap_id"] is not None
    r = client.post(
        f"/api/v1/knowledge/gaps/{g['gap_id']}/answer",
        json={"answer": "新答案", "staff_id": 1},
    ).json()["data"]
    assert r["status"] == "pending"
    c = client.post(
        f"/api/v1/knowledge/{r['knowledge_id']}/confirm", json={"staff_id": 1}
    ).json()["data"]
    assert c["status"] == "confirmed"
    assert c["resolved_gap_id"] == g["gap_id"]
