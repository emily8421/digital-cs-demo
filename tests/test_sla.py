"""Sprint-11 SLA 时效测试（REQ-14）：扫描超时未答。

SQLite 内存库。真实端到端（POST /sla/scan）见 08 Sprint-11 验收记录。
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import Conversation, Message, Staff
from backend.app.service.sla.scanner import scan_sla


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    S = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = S()
    s.add(Staff(name="陈总", role="owner", active=True))
    s.commit()
    yield s
    s.close()


def _msg(db, conv_id, direction, minutes_ago, content="x"):
    db.add(
        Message(
            conversation_id=conv_id,
            direction=direction,
            channel="sim",
            sender_external_id="c",
            content_type="text",
            content_text=content,
            received_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        )
    )
    db.commit()


def _conv(db, group="g1"):
    c = Conversation(external_group_id=group, last_active_at=datetime.now(timezone.utc))
    db.add(c)
    db.commit()
    return c


def test_overdue_unanswered(db):
    c = _conv(db)
    _msg(db, c.id, "inbound", 60)  # 60 分钟前客户消息，无应答
    r = scan_sla(db, threshold_minutes=30)
    assert r.count == 1
    assert r.overdues[0].group == "g1"
    assert r.overdues[0].overdue_minutes >= 60


def test_answered_not_overdue(db):
    c = _conv(db)
    _msg(db, c.id, "inbound", 60)
    _msg(db, c.id, "outbound", 50)  # 50 分钟前应答（晚于 inbound）→ 已答
    r = scan_sla(db, threshold_minutes=30)
    assert r.count == 0


def test_within_threshold_not_overdue(db):
    c = _conv(db)
    _msg(db, c.id, "inbound", 10)  # 10 分钟前，未超 30 阈值
    r = scan_sla(db, threshold_minutes=30)
    assert r.count == 0


def test_prompt_and_notification_written(db):
    c = _conv(db)
    _msg(db, c.id, "inbound", 60)
    r = scan_sla(db, threshold_minutes=30)
    assert r.prompt and "未回复" in r.prompt
    assert r.notification_id is not None  # 写了 Notification(kind=sla)
