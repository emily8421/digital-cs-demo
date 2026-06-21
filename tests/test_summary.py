"""REQ-7 小结单测：聚合消息/转交 → 口语化小结 + notification(kind=summary)。SQLite 内存库。"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import Conversation, Handoff, Message, Notification, Staff
from backend.app.service.summary.generator import generate_daily_summary


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    s.add(Staff(name="陈总", role="owner", active=True))
    s.add(Staff(name="小雯", role="sales", active=True))
    s.commit()
    yield s
    s.close()


def _msg(db, conv_id, ctype="text"):
    db.add(
        Message(
            conversation_id=conv_id,
            direction="inbound",
            channel="simulator",
            sender_external_id="c",
            content_type=ctype,
            content_text="x" if ctype == "text" else None,
            received_at=datetime.now(timezone.utc),
        )
    )


def test_summary_aggregates_messages_and_followups(db):
    """聚合消息量/类型 + open 转交清单 → 小结含总量/类型/分配对象；落 summary 通知给 owner。"""
    conv = Conversation(external_group_id="g1", last_active_at=datetime.now(timezone.utc))
    db.add(conv)
    db.flush()
    _msg(db, conv.id, "text")
    _msg(db, conv.id, "text")
    _msg(db, conv.id, "voice")
    xiaowen = db.query(Staff).filter_by(name="小雯").first()
    db.add(
        Handoff(
            conversation_id=conv.id,
            scenario="presale",
            target_staff_id=xiaowen.id,
            reason="x",
            status="open",
        )
    )
    db.commit()

    res = generate_daily_summary(db)
    db.commit()
    assert res.summary.startswith("今天共 3 条客户消息")
    assert "文字2条" in res.summary and "语音1条" in res.summary
    assert "1 条需跟进" in res.summary
    assert "售前(小雯)" in res.summary

    n = db.get(Notification, res.notification_id)
    assert n.kind == "summary"
    owner = db.query(Staff).filter_by(role="owner").first()
    assert n.target_staff_id == owner.id


def test_summary_empty_friendly(db):
    """无消息时友好口径（非报表腔）。"""
    res = generate_daily_summary(db)
    db.commit()
    assert "还没有客户消息" in res.summary
