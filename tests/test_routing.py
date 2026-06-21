"""REQ-5/8 路由与通知单测：scenario→role→staff、规则缺失兜底、口语化 body。SQLite 内存库。"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import RoutingRule, Staff
from backend.app.service.routing.notifier import build_handoff_body
from backend.app.service.routing.router import resolve_target


@pytest.fixture()
def db():
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
    yield s
    s.close()


def test_resolve_hits_staff(db):
    t = resolve_target(db, "presale")
    assert t.role == "sales"
    assert t.staff_name == "小雯"
    assert t.staff_id is not None


def test_resolve_unknown_scenario(db):
    t = resolve_target(db, "nope")
    assert t.role is None and t.staff_id is None


def test_resolve_no_active_staff(db):
    db.query(Staff).filter_by(role="owner").update({"active": False})
    db.commit()
    t = resolve_target(db, "unknown_question")
    assert t.role == "owner"  # 规则命中
    assert t.staff_id is None  # 但无在岗员工


def test_build_body_with_contact():
    body = build_handoff_body(
        staff_name="小雯",
        scenario="presale",
        reason="客户询价需跟进",
        customer="sim_group_001",
        masked_contact="139****5678",
    )
    assert "小雯" in body and "客户询价需跟进" in body
    assert "sim_group_001" in body and "139****5678" in body


def test_build_body_no_staff_no_contact():
    body = build_handoff_body(
        staff_name=None, scenario="presale", reason="x", customer="g1", masked_contact=None
    )
    assert "相关同事" in body  # 无 staff_name 兜底
    assert "139" not in body  # 无联系方式
