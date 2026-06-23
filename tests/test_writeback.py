"""Sprint-10 知识回写测试（REQ-13）：缺口 → pending → confirmed + gap resolved。

SQLite 内存库 + fake embedder（不依赖 TEI/pgvector）。
真实端到端（TEI+检索命中新条目）见 08 Sprint-10 验收记录。
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base
from backend.app.models import KnowledgeGap
from backend.app.service.knowledge.writeback import (
    answer_gap,
    confirm_knowledge,
    list_open_gaps,
    list_pending,
)


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


def _fake_embedder():
    return lambda text: [0.1] * 8  # 固定向量（SQLite 存 JSON，测试不查距离）


def test_answer_gap_creates_pending_and_links(db):
    g = KnowledgeGap(conversation_id=1, question_text="灯带能在海底用吗")
    db.add(g)
    db.flush()
    item = answer_gap(db, g.id, "不支持水下长期使用", staff_id=2, embedder=_fake_embedder())
    assert item.status == "pending"
    assert item.question_pattern == "灯带能在海底用吗"
    assert item.source_staff_id == 2
    db.flush()
    db.refresh(g)
    assert g.resolved_knowledge_id == item.id  # 关联
    assert g.status == "open"  # 还没 resolved（等 confirm）


def test_confirm_flips_to_confirmed_and_resolves_gap(db):
    g = KnowledgeGap(conversation_id=1, question_text="q")
    db.add(g)
    db.flush()
    item = answer_gap(db, g.id, "答案", staff_id=2, embedder=_fake_embedder())
    db.flush()
    confirmed, gap_id = confirm_knowledge(db, item.id, staff_id=3)
    assert confirmed.status == "confirmed"
    assert confirmed.source_staff_id == 3
    assert gap_id == g.id
    db.refresh(g)
    assert g.status == "resolved"


def test_answer_gap_missing_returns_none(db):
    assert answer_gap(db, 999, "x", staff_id=1, embedder=_fake_embedder()) is None


def test_confirm_non_pending_returns_none(db):
    assert confirm_knowledge(db, 999, staff_id=1) == (None, None)


def test_list_open_gaps_and_pending(db):
    g = KnowledgeGap(conversation_id=1, question_text="q1")
    db.add(g)
    db.flush()
    answer_gap(db, g.id, "a1", staff_id=1, embedder=_fake_embedder())
    db.flush()
    assert len(list_open_gaps(db)) == 1  # gap 仍 open（confirm 前）
    assert len(list_pending(db)) == 1
