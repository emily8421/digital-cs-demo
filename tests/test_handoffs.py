"""REQ-4/5/8 集成：投递含手机号消息→留资；POST /handoffs→路由+口语化通知。SQLite + TestClient。"""
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
    s.add(Staff(name="小雯", role="sales", active=True))
    s.add(RoutingRule(scenario="presale", target_role="sales"))
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


def test_simulate_with_phone_creates_lead(client):
    """投递含手机号消息 → 产生留资记录（lead_id 非空）。"""
    r = client.post(
        "/api/v1/messages/simulate",
        json={
            "external_group_id": "g1",
            "sender_external_id": "cust",
            "content_text": "想订货，电话13912345678",
        },
    )
    assert r.status_code == 200
    assert r.json()["data"]["lead_id"] is not None


def test_handoff_routes_and_notifies(client):
    """触发转交 → 路由到 sales/小雯 + 落通知 + body 含摘要与脱敏联系方式。"""
    conv_id = client.post(
        "/api/v1/messages/simulate",
        json={
            "external_group_id": "g1",
            "sender_external_id": "cust",
            "content_text": "询价 13912345678",
        },
    ).json()["data"]["conversation_id"]

    r = client.post(
        "/api/v1/handoffs",
        json={
            "conversation_id": conv_id,
            "scenario": "presale",
            "reason": "客户询盘需跟进报价",
        },
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["target_role"] == "sales"
    assert d["staff_name"] == "小雯"
    assert d["notification_id"]
    assert "小雯" in d["body"]
    assert "139****5678" in d["body"]  # 口语化通知含脱敏联系方式


def test_handoff_unknown_scenario_fallback(client):
    """无路由规则的场景 → role/staff 为空，body 兜底为「相关同事」。"""
    conv_id = client.post(
        "/api/v1/messages/simulate",
        json={"external_group_id": "g2", "sender_external_id": "c", "content_text": "hi"},
    ).json()["data"]["conversation_id"]
    r = client.post(
        "/api/v1/handoffs",
        json={"conversation_id": conv_id, "scenario": "weird", "reason": "x"},
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["target_role"] is None
    assert "相关同事" in d["body"]
