"""REQ-2/3 检索逻辑单测：select_hits 的阈值过滤 / 排序 / 未命中。

纯函数测试，**不依赖 PostgreSQL / Docker / torch**（检索的 DB+向量部分
由真实 PG 端到端验证覆盖，见 docs/08-dev-plan.md Sprint-2 验收记录）。
"""
import os

# import app 前先指向 sqlite，避免 lifespan 的 init_db 去连真实 PG
os.environ.setdefault("DATABASE_URL", "sqlite://")

from types import SimpleNamespace

from backend.app.service.knowledge.search import select_hits


def _item(id: int, qp: str = "q", answer: str = "a", status: str = "confirmed"):
    """轻量模拟 KnowledgeItem（鸭子类型，select_hits 只读这几个字段）。"""
    return SimpleNamespace(
        id=id, question_pattern=qp, answer=answer, status=status
    )


def test_filters_below_threshold():
    """score 低于阈值的条目被过滤。"""
    candidates = [(_item(1), 0.9), (_item(2), 0.5), (_item(3), 0.7)]
    hits = select_hits(candidates, threshold=0.7)
    assert [h.id for h in hits] == [1, 3]


def test_sorted_by_score_desc():
    """命中条目按 score 降序。"""
    candidates = [(_item(1), 0.7), (_item(2), 0.95), (_item(3), 0.8)]
    hits = select_hits(candidates, threshold=0.7)
    assert [h.id for h in hits] == [2, 3, 1]


def test_empty_when_none_above_threshold():
    """全部低于阈值 → 未命中（hit=False, items=[]）。"""
    candidates = [(_item(1), 0.3), (_item(2), 0.4)]
    assert select_hits(candidates, threshold=0.7) == []


def test_score_rounded_to_4_decimals():
    """score 保留 4 位小数（07 §3.2 出参口径）。"""
    hits = select_hits([(_item(1), 0.912345)], threshold=0.7)
    assert hits[0].score == 0.9123


def test_carries_through_fields():
    """命中结果携带 question_pattern / answer / status。"""
    hits = select_hits([(_item(7, qp="IP65区别", answer="防喷水", status="confirmed"), 0.9)], threshold=0.7)
    h = hits[0]
    assert h.question_pattern == "IP65区别"
    assert h.answer == "防喷水"
    assert h.status == "confirmed"
