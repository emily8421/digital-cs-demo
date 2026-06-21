"""REQ-6 编排单测：act_on_search 命中作答 / 未命中缺口+转交。

注入 fake 检索结果，SQLite 内存库，**不依赖 TEI/pgvector**（编排的检索步骤由端到端覆盖）。
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import Conversation, KnowledgeGap, Message, RoutingRule, Staff
from backend.app.service.conversation.engine import act_on_search
from backend.app.service.knowledge.search import KnowledgeHit


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    s.add(Staff(name="陈总", role="owner", active=True))
    s.add(RoutingRule(scenario="unknown_question", target_role="owner"))
    s.commit()
    yield s
    s.close()


def _conv(db):
    c = Conversation(external_group_id="g1", last_active_at=datetime.now(timezone.utc))
    db.add(c)
    db.flush()
    return c


def _hit_item(answer="IP65 防喷水，IP67 可短时浸水。"):
    return KnowledgeHit(
        id=1, question_pattern="IP65/67区别", answer=answer, score=0.9, status="confirmed"
    )


def test_act_hit_writes_answer_outbound(db):
    """命中→写 outbound 作答（回标准答案），无缺口。"""
    c = _conv(db)
    res = act_on_search(db, c, "IP67能做吗", "simulator", hit=True, items=[_hit_item()])
    db.commit()
    assert res.hit is True
    assert res.reply_text == "IP65 防喷水，IP67 可短时浸水。"
    assert res.gap_id is None
    outbound = db.query(Message).filter_by(direction="outbound").one()
    assert outbound.content_text == res.reply_text


def test_act_miss_creates_gap_and_handoff(db):
    """未命中→写 gap(open)+outbound 请留资+转交 owner+通知。"""
    c = _conv(db)
    res = act_on_search(db, c, "你们灯带能用在海里吗", "simulator", hit=False, items=[])
    db.commit()
    assert res.hit is False
    assert res.gap_id is not None
    assert res.handoff_id is not None
    assert res.notification_id is not None

    gap = db.get(KnowledgeGap, res.gap_id)
    assert gap.status == "open"
    assert "海里" in gap.question_text

    outbound = db.query(Message).filter_by(direction="outbound").one()
    assert "联系方式" in outbound.content_text or "留" in outbound.content_text  # 请留资口径
