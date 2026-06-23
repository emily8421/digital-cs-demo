"""知识库检索接口（docs/07-api-spec.md §3.2）。

GET /api/v1/knowledge/search?q= → { hit, items:[{id,question_pattern,answer,score,status}] }。
未命中 hit:false, items:[]（编排据此走缺口流程 REQ-6，见 Sprint-4）。
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import (
    ApiResponse,
    KnowledgeAnswerData,
    KnowledgeAnswerRequest,
    KnowledgeConfirmData,
    KnowledgeConfirmRequest,
    KnowledgeGapListData,
    KnowledgeGapOut,
    KnowledgeItemOut,
    KnowledgePendingItemOut,
    KnowledgePendingListData,
    KnowledgeSearchData,
)
from ..service.knowledge.search import search
from ..service.knowledge.writeback import (
    answer_gap,
    confirm_knowledge,
    list_open_gaps,
    list_pending,
)

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
        ),
    )


@router.get("/gaps", response_model=ApiResponse[KnowledgeGapListData])
def list_gaps(db: Session = Depends(get_db)):
    """列 open 缺口（供拍板人补答，REQ-13）。"""
    gaps = list_open_gaps(db)
    return ApiResponse(data=KnowledgeGapListData(gaps=gaps))


@router.post("/gaps/{gap_id}/answer", response_model=ApiResponse[KnowledgeAnswerData])
def answer_knowledge_gap(
    gap_id: int, body: KnowledgeAnswerRequest, db: Session = Depends(get_db)
):
    """拍板人对缺口补答 → 创建 pending 条目（关联 gap，REQ-13）。"""
    item = answer_gap(db, gap_id, body.answer, body.staff_id)
    if item is None:
        raise HTTPException(404, "缺口不存在或已处理")
    db.commit()
    return ApiResponse(data=KnowledgeAnswerData(knowledge_id=item.id, status=item.status))


@router.get("/pending", response_model=ApiResponse[KnowledgePendingListData])
def list_pending_knowledge(db: Session = Depends(get_db)):
    """列 pending 条目（供拍板人确认，REQ-13）。"""
    items = list_pending(db)
    return ApiResponse(data=KnowledgePendingListData(items=items))


@router.post("/{item_id}/confirm", response_model=ApiResponse[KnowledgeConfirmData])
def confirm_knowledge_item(
    item_id: int, body: KnowledgeConfirmRequest, db: Session = Depends(get_db)
):
    """拍板人确认 pending → confirmed + 回填 gap（REQ-13）。"""
    item, gap_id = confirm_knowledge(db, item_id, body.staff_id)
    if item is None:
        raise HTTPException(404, "条目不存在或非 pending")
    db.commit()
    return ApiResponse(
        data=KnowledgeConfirmData(id=item.id, status=item.status, resolved_gap_id=gap_id)
    )
