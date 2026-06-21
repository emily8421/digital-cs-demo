"""消息与会话接口（docs/07-api-spec.md §2 / §3.1）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..channels.simulator import simulator_channel
from ..db import get_db
from ..models import Conversation
from ..schemas import (
    ApiResponse,
    ConversationListItem,
    ConversationOut,
    SimulateData,
    SimulateRequest,
)
from ..service.orchestrator import handle_inbound

router = APIRouter(prefix="/api/v1", tags=["messages"])


@router.post("/messages/simulate", response_model=ApiResponse[SimulateData])
def simulate(req: SimulateRequest, db: Session = Depends(get_db)):
    """模拟器投递一条入站消息 → 归一化 → 入库 + 留资抽取；返回 message_id / conversation_id / lead_id。"""
    normalized = simulator_channel.receive(req.model_dump())
    message_id, conversation_id, lead_id = handle_inbound(db, normalized, channel_name="simulator")
    return ApiResponse(
        data=SimulateData(
            message_id=message_id, conversation_id=conversation_id, lead_id=lead_id
        )
    )


@router.get("/conversations", response_model=ApiResponse[list[ConversationListItem]])
def list_conversations(db: Session = Depends(get_db)):
    items = db.query(Conversation).order_by(Conversation.last_active_at.desc()).all()
    return ApiResponse(data=items)


@router.get("/conversations/{conversation_id}", response_model=ApiResponse[ConversationOut])
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    return ApiResponse(data=conv)
