"""Sprint-12 话题级暂停测试（REQ-10）：topic_handed_off 判定。

SQLite 内存库。真实端到端（POST /topic-handoff + simulate）见 08 Sprint-12 验收记录。
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import Conversation, TopicHandoff
from backend.app.service.conversation.engine import topic_handed_off


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    S = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = S()
    yield s
    s.close()


def _conv(db, group="g1"):
    c = Conversation(external_group_id=group, last_active_at=datetime.now(timezone.utc))
    db.add(c)
    db.commit()
    return c


def test_topic_not_handed_off_by_default(db):
    c = _conv(db)
    assert topic_handed_off(db, c.id, "cust_A") is False


def test_topic_handed_off_only_that_topic(db):
    c = _conv(db)
    db.add(TopicHandoff(conversation_id=c.id, topic_key="cust_A", handoff_state="handed_off"))
    db.commit()
    assert topic_handed_off(db, c.id, "cust_A") is True  # 该话题暂停
    assert topic_handed_off(db, c.id, "cust_B") is False  # 其他话题正常


def test_topic_auto_not_paused(db):
    c = _conv(db)
    db.add(TopicHandoff(conversation_id=c.id, topic_key="cust_A", handoff_state="auto"))
    db.commit()
    assert topic_handed_off(db, c.id, "cust_A") is False  # auto 不暂停


def test_topic_isolated_per_conversation(db):
    c1 = _conv(db, "g1")
    c2 = _conv(db, "g2")
    db.add(TopicHandoff(conversation_id=c1.id, topic_key="cust_A", handoff_state="handed_off"))
    db.commit()
    assert topic_handed_off(db, c1.id, "cust_A") is True
    assert topic_handed_off(db, c2.id, "cust_A") is False  # 不同会话，互不影响
