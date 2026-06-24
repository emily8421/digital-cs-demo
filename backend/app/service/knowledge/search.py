"""知识检索：query → embedding → pgvector 相似检索 → 阈值判定命中/未命中。

对应 docs/design/knowledge-base.md §2、docs/07-api-spec.md §3.2。
命中口径：status=confirmed 且 cosine 相似度 ≥ 阈值；未命中 hit=False。
"""
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...config import settings
from ...models import KnowledgeItem
from .embedder import Embedder, embed as default_embed


@dataclass
class KnowledgeHit:
    """检索命中的单条结果（带 score）。"""

    id: int
    question_pattern: str
    answer: str
    score: float
    status: str


def select_hits(
    candidates: list[tuple[KnowledgeItem, float]], threshold: float
) -> list[KnowledgeHit]:
    """纯函数：从 (item, score) 候选里筛 score≥阈值，按 score 降序。

    抽出来便于无 DB / 无向量依赖的单元测试（阈值过滤、排序、hit 布尔判定）。
    """
    kept = [(it, sc) for it, sc in candidates if sc >= threshold]
    kept.sort(key=lambda x: x[1], reverse=True)
    return [
        KnowledgeHit(
            id=it.id,
            question_pattern=it.question_pattern,
            answer=it.answer,
            score=round(sc, 4),
            status=it.status,
        )
        for it, sc in kept
    ]


def search(
    db: Session,
    q: str,
    *,
    embedder: Embedder | None = None,
    threshold: float | None = None,
) -> tuple[bool, list[KnowledgeHit]]:
    """检索 confirmed 知识条目。返回 (hit, items)；未命中 hit=False, items=[]。

    embedder / threshold 可注入，默认取配置（进程内 BGE、阈值 0.7）。
    """
    if threshold is None:
        threshold = settings.knowledge_score_threshold
    if embedder is None:
        embedder = default_embed

    query_vec = embedder(q)
    # pgvector cosine 距离 <=> ；相似度 score = 1 - distance
    distance = KnowledgeItem.embedding.cosine_distance(query_vec)
    stmt = (
        select(KnowledgeItem, distance.label("distance"))
        .where(KnowledgeItem.status == "confirmed")
        .order_by(distance)
        .limit(20)
    )
    rows = db.execute(stmt).all()
    candidates = [(row[0], 1.0 - row[1]) for row in rows]
    hits = select_hits(candidates, threshold)
    return (len(hits) > 0, hits)
