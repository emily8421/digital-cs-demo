"""知识回写（REQ-13，Sprint-10）。对应 docs/design-knowledge-base.md §3.1。

拍板人补答缺口 → pending（+embedding，关联 gap）→ 确认 → confirmed + gap resolved。
**回写必经拍板人确认，不自动固化。**

- answer_gap / confirm_knowledge：db 副作用；answer_gap 可注入 embedder（测试用 fake）。
- list_open_gaps / list_pending：查询，供确认页面。
"""
from sqlalchemy.orm import Session

from ...models import KnowledgeGap, KnowledgeItem
from .embedder import Embedder, embed as default_embed


def answer_gap(
    db: Session,
    gap_id: int,
    answer: str,
    staff_id: int,
    embedder: Embedder | None = None,
) -> KnowledgeItem | None:
    """拍板人对 open 缺口补答 → 创建 pending 条目（+embedding，关联 gap）。

    返回新建 pending 条目；缺口不存在或已处理则返回 None。
    gap.status 暂不动（等 confirm_knowledge 时转 resolved），仅 resolved_knowledge_id 关联。
    """
    if embedder is None:
        embedder = default_embed
    gap = db.query(KnowledgeGap).filter_by(id=gap_id, status="open").first()
    if gap is None:
        return None
    vec = embedder(gap.question_text)
    item = KnowledgeItem(
        question_pattern=gap.question_text,
        answer=answer,
        embedding=vec,
        status="pending",
        source_staff_id=staff_id,
    )
    db.add(item)
    db.flush()
    gap.resolved_knowledge_id = item.id  # 关联（confirm 时 gap 转 resolved）
    db.flush()
    return item


def confirm_knowledge(
    db: Session, item_id: int, staff_id: int
) -> tuple[KnowledgeItem | None, int | None]:
    """拍板人确认 pending → confirmed + 关联 gap resolved。返回 (item, resolved_gap_id)。

    条目不存在或非 pending 返回 (None, None)。
    """
    item = db.query(KnowledgeItem).filter_by(id=item_id, status="pending").first()
    if item is None:
        return None, None
    item.status = "confirmed"
    item.source_staff_id = staff_id
    gap = db.query(KnowledgeGap).filter_by(resolved_knowledge_id=item_id).first()
    resolved_gap_id = None
    if gap:
        gap.status = "resolved"
        resolved_gap_id = gap.id
    db.flush()
    return item, resolved_gap_id


def list_open_gaps(db: Session) -> list[KnowledgeGap]:
    """列 open 缺口（供拍板人补答）。"""
    return (
        db.query(KnowledgeGap)
        .filter_by(status="open")
        .order_by(KnowledgeGap.id.desc())
        .all()
    )


def list_pending(db: Session) -> list[KnowledgeItem]:
    """列 pending 条目（供拍板人确认）。"""
    return (
        db.query(KnowledgeItem)
        .filter_by(status="pending")
        .order_by(KnowledgeItem.id.desc())
        .all()
    )
