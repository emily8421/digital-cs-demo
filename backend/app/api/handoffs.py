"""人工转交接口（docs/07-api-spec.md §3.3）。

POST /api/v1/handoffs：建转交记录 + 路由解析到目标角色/员工 + 生成口语化通知。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Conversation, Handoff, Lead
from ..schemas import ApiResponse, HandoffData, HandoffRequest
from ..service.routing.notifier import build_handoff_body, notify_handoff
from ..service.routing.router import resolve_target

router = APIRouter(prefix="/api/v1", tags=["handoffs"])


@router.post("/handoffs", response_model=ApiResponse[HandoffData])
def create_handoff(req: HandoffRequest, db: Session = Depends(get_db)):
    """触发一次转交：按 scenario 路由到目标员工，落 handoff + 口语化通知。"""
    conv = db.get(Conversation, req.conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")

    target = resolve_target(db, req.scenario)

    handoff = Handoff(
        conversation_id=req.conversation_id,
        scenario=req.scenario,
        target_staff_id=target.staff_id,
        reason=req.reason,
        context_ref=req.context_ref,
        status="open",
    )
    db.add(handoff)
    db.flush()

    # 取该会话最近一条留资（若有），把脱敏联系方式附进通知
    lead = (
        db.query(Lead)
        .filter_by(conversation_id=req.conversation_id)
        .order_by(Lead.id.desc())
        .first()
    )
    body = build_handoff_body(
        staff_name=target.staff_name,
        scenario=req.scenario,
        reason=req.reason,
        customer=conv.external_group_id,
        masked_contact=lead.contact_value_masked if lead else None,
    )
    notification = notify_handoff(
        db, staff_id=target.staff_id, body=body, ref_handoff_id=handoff.id
    )

    db.commit()
    db.refresh(handoff)
    db.refresh(notification)
    return ApiResponse(
        data=HandoffData(
            handoff_id=handoff.id,
            target_staff_id=target.staff_id,
            target_role=target.role,
            notification_id=notification.id,
            staff_name=target.staff_name,
            body=body,
        )
    )
