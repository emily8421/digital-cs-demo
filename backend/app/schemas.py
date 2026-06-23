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
    lead_id: Optional[int] = None  # 留资记录 id（REQ-4）；无联系方式时为 None
    # 编排结果（Sprint-4）；orchestration 被跳过时全为 None
    hit: Optional[bool] = None
    reply_text: Optional[str] = None
    gap_id: Optional[int] = None
    handoff_id: Optional[int] = None
    notification_id: Optional[int] = None


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


class KnowledgeItemOut(BaseModel):
    """知识检索命中条目（07 §3.2）。"""

    id: int
    question_pattern: str
    answer: str
    score: float
    status: str


class KnowledgeSearchData(BaseModel):
    hit: bool
    items: list[KnowledgeItemOut]


class KnowledgeGapOut(BaseModel):
    """知识缺口（供拍板人补答，07 §3.5）。"""

    model_config = {"from_attributes": True}
    id: int
    question_text: str
    detected_at: datetime


class KnowledgeGapListData(BaseModel):
    gaps: list[KnowledgeGapOut]


class KnowledgeAnswerRequest(BaseModel):
    """拍板人对缺口补答（07 §3.5）。"""

    answer: str
    staff_id: int


class KnowledgeAnswerData(BaseModel):
    knowledge_id: int
    status: str


class KnowledgePendingItemOut(BaseModel):
    """待确认条目（供拍板人确认，07 §3.5）。"""

    model_config = {"from_attributes": True}
    id: int
    question_pattern: str
    answer: str
    source_staff_id: Optional[int] = None


class KnowledgePendingListData(BaseModel):
    items: list[KnowledgePendingItemOut]


class KnowledgeConfirmRequest(BaseModel):
    """拍板人确认 pending→confirmed（07 §3.5）。"""

    staff_id: int


class KnowledgeConfirmData(BaseModel):
    id: int
    status: str
    resolved_gap_id: Optional[int] = None


class HandoffRequest(BaseModel):
    """转交请求体（07 §3.3）。"""

    conversation_id: int
    scenario: str
    reason: str
    context_ref: Optional[dict] = None


class HandoffData(BaseModel):
    """转交响应（07 §3.3）：路由解析 + 通知结果。"""

    handoff_id: int
    target_staff_id: Optional[int] = None
    target_role: Optional[str] = None
    staff_name: Optional[str] = None
    notification_id: int
    body: str  # 生成的口语化提醒（便于查看/验证）


class HandoffStateRequest(BaseModel):
    """置/解除转人工暂停（REQ-10）。"""

    handoff_state: str = Field(pattern="^(auto|handed_off)$")


class HandoffStateData(BaseModel):
    conversation_id: int
    handoff_state: str


class SummaryData(BaseModel):
    """定时小结响应（07 §3.4）。"""

    notification_id: int
    summary: str
