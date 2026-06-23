"""SLA 时效扫描接口（docs/07-api-spec.md §3.5）。

POST /api/v1/sla/scan：手动触发（或部署层 cron 定时调），扫描超时未答的客户消息。
应用不内嵌调度（见 05：调度=外部 cron），同 summaries。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ApiResponse, OverdueItemOut, SLAScanData, SLAScanRequest
from ..service.sla.scanner import scan_sla

router = APIRouter(prefix="/api/v1/sla", tags=["sla"])


@router.post("/scan", response_model=ApiResponse[SLAScanData])
def scan_sla_endpoint(body: SLAScanRequest | None = None, db: Session = Depends(get_db)):
    """扫描超时未答的客户消息 + 提示经营者（REQ-14）。"""
    threshold = body.threshold_minutes if body else None
    result = scan_sla(db, threshold)
    db.commit()
    return ApiResponse(
        data=SLAScanData(
            overdues=[
                OverdueItemOut(
                    conversation_id=o.conversation_id,
                    group=o.group,
                    message_id=o.message_id,
                    overdue_minutes=o.overdue_minutes,
                )
                for o in result.overdues
            ],
            count=result.count,
            notification_id=result.notification_id,
            prompt=result.prompt,
        )
    )
