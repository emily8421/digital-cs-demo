"""知识库检索接口（docs/07-api-spec.md §3.2）。

GET /api/v1/knowledge/search?q= → { hit, items:[{id,question_pattern,answer,score,status}] }。
未命中 hit:false, items:[]（编排据此走缺口流程 REQ-6，见 Sprint-4）。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ApiResponse, KnowledgeItemOut, KnowledgeSearchData
from ..service.knowledge.search import search

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.get("/search", response_model=ApiResponse[KnowledgeSearchData])
def search_knowledge(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """知识检索（单轮，REQ-2/3）。"""
    hit, hits = search(db, q)
    return ApiResponse(
        data=KnowledgeSearchData(
            hit=hit,
            items=[
                KnowledgeItemOut(
                    id=h.id,
                    question_pattern=h.question_pattern,
                    answer=h.answer,
                    score=h.score,
                    status=h.status,
                )
                for h in hits
            ],
        )
    )
