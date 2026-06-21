"""Pydantic 入参/出参 + 统一响应格式（docs/07-api-spec.md §1）。"""
from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应：{ code, message, data }。code=0 成功。"""

    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


class SimulateRequest(BaseModel):
    """模拟器投递入站消息的请求体（07 §3.1）。"""

    external_group_id: str
    sender_external_id: str
    content_type: str = Field(default="text", pattern="^(text|voice|image|video|other)$")
    content_text: Optional[str] = None
    received_at: Optional[datetime] = None  # 不传则取当前时间


class SimulateData(BaseModel):
    message_id: int
    conversation_id: int


class MessageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    direction: str
    channel: str
    sender_external_id: str
    content_type: str
    content_text: Optional[str] = None
    received_at: datetime


class ConversationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    external_group_id: str
    handoff_state: str
    last_active_at: datetime
    messages: list[MessageOut] = []


class ConversationListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    external_group_id: str
    handoff_state: str
    last_active_at: datetime
