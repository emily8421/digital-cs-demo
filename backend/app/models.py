"""ORM 模型，对应 docs/06-db-design.md 的 dcs_conversations / dcs_messages（Sprint-1 范围）。

注意：只落地这两张表。其余表（knowledge/leads/handoffs/...）随各自 Sprint 加入。
"""
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(Base):
    """会话（群/话题）与会话级状态。对应 dcs_conversations。"""

    __tablename__ = "dcs_conversations"
    __table_args__ = (
        CheckConstraint(
            "handoff_state IN ('auto','handed_off')", name="ck_conversations_handoff"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    external_group_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    topic_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # P1：会话级暂停（REQ-10）消费此字段；话题级精化留后续
    handoff_state: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", order_by="Message.received_at"
    )


class Message(Base):
    """入站/出站消息（归一化后）。对应 dcs_messages。"""

    __tablename__ = "dcs_messages"
    __table_args__ = (
        CheckConstraint("direction IN ('inbound','outbound')", name="ck_messages_direction"),
        CheckConstraint(
            "content_type IN ('text','voice','image','video','other')",
            name="ck_messages_content_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # inbound/outbound
    channel: Mapped[str] = mapped_column(String(32), nullable=False)  # simulator/wework/...
    sender_external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    content_type: Mapped[str] = mapped_column(String(16), nullable=False)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
