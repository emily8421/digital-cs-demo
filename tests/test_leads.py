"""REQ-4 留资识别单测：手机号抽取 / 脱敏 / 无号码不产生记录。SQLite 内存库。"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import Conversation, Lead
from backend.app.service.leads.detector import find_phone, mask_phone
from backend.app.service.leads.service import capture_lead


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    s = Session()
    yield s
    s.close()


def _conv(db):
    c = Conversation(external_group_id="g1", last_active_at=datetime.now(timezone.utc))
    db.add(c)
    db.flush()
    return c


def test_find_and_mask_phone():
    assert find_phone("我手机13800138000，方便联系") == "13800138000"
    assert find_phone("没有号码的文本") is None
    assert find_phone(None) is None
    assert mask_phone("13800138000") == "138****8000"


def test_capture_lead_writes_masked(db):
    c = _conv(db)
    lead = capture_lead(db, c.id, "订货联系13912345678")
    db.commit()
    assert lead is not None
    assert lead.contact_value_masked == "139****5678"
    assert lead.contact_value_enc is None  # 加密原文待后续实现
    assert lead.contact_type == "phone"


def test_capture_lead_no_phone_no_record(db):
    c = _conv(db)
    lead = capture_lead(db, c.id, "这条没有联系方式")
    db.commit()
    assert lead is None
    assert db.query(Lead).count() == 0
