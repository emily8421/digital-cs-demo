"""定时小结接口（docs/07-api-spec.md §3.4）。

POST /api/v1/summaries/daily：手动触发（或由部署层 cron 定时调用）生成经营者小结。
应用不内嵌调度（见 docs/05-tech-spec.md：调度=外部 cron）。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ApiResponse, SummaryData
from ..service.summary.generator import generate_daily_summary

router = APIRouter(prefix="/api/v1", tags=["summaries"])


@router.post("/summaries/daily", response_model=ApiResponse[SummaryData])
def trigger_daily_summary(db: Session = Depends(get_db)):
    """生成并发送当日小结（REQ-7）。本机手动触发；生产由 cron 定时调本接口。"""
    result = generate_daily_summary(db)
    db.commit()
    return ApiResponse(
        data=SummaryData(
            notification_id=result.notification_id, summary=result.summary
        )
    )
