"""ORM 模型，对应 docs/06-db-design.md。

- dcs_conversations / dcs_messages（Sprint-1）
- dcs_knowledge_items（Sprint-2）
- dcs_leads / dcs_staff / dcs_routing_rules / dcs_handoffs / dcs_notifications（Sprint-3）
- dcs_knowledge_gaps（Sprint-4）
其余表随各自 Sprint 加入。
"""
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
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


class KnowledgeItem(Base):
    """知识条目（FAQ/参数/选型）及其确认状态。对应 dcs_knowledge_items。"""

    __tablename__ = "dcs_knowledge_items"
    __table_args__ = (
        CheckConstraint("status IN ('confirmed','pending')", name="ck_knowledge_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    question_pattern: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # 向量：PG 用 pgvector 的 vector(512)；SQLite 退化为 JSON（无 Docker 单测也能建表）
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(512).with_variant(JSON, "sqlite"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="confirmed")
    # 来源确认人；dcs_staff 表在 Sprint-3 建，本轮先 nullable、不加 FK（预置种子为 NULL）
    source_staff_id: Mapped[int | None] = mapped_column(nullable=True)
    # P2 知识回写：补答人=source_staff_id（answer_gap 写），确认人=confirmed_by_staff_id（confirm 写），互不覆盖
    confirmed_by_staff_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )


class Staff(Base):
    """员工花名册与角色。对应 dcs_staff。REQ-5/8。"""

    __tablename__ = "dcs_staff"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # sales/tech/merchandiser/owner
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 接收提醒的外部标识
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RoutingRule(Base):
    """场景→角色路由规则。对应 dcs_routing_rules。REQ-8。"""

    __tablename__ = "dcs_routing_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    target_role: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Lead(Base):
    """客户留资（联系方式，脱敏存储）。对应 dcs_leads。REQ-4。"""

    __tablename__ = "dcs_leads"
    __table_args__ = (
        CheckConstraint(
            "contact_type IN ('phone','wechat','email','other')", name="ck_leads_contact_type"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    contact_type: Mapped[str] = mapped_column(String(16), nullable=False)
    contact_value_masked: Mapped[str] = mapped_column(String(64), nullable=False)  # 脱敏值（如 138****6677）
    # 加密原文（合规存储）；Sprint-3 暂不实现加密，留 NULL（需密钥管理，待后续）
    contact_value_enc: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class Handoff(Base):
    """转人工/转交记录。对应 dcs_handoffs。REQ-5/8。"""

    __tablename__ = "dcs_handoffs"
    __table_args__ = (
        CheckConstraint("status IN ('open','accepted','closed')", name="ck_handoffs_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    scenario: Mapped[str] = mapped_column(String(32), nullable=False)
    target_staff_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcs_staff.id"), nullable=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    context_ref: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )


class Notification(Base):
    """出站提醒/小结的发送记录。对应 dcs_notifications。REQ-5/7。"""

    __tablename__ = "dcs_notifications"
    __table_args__ = (
        CheckConstraint("kind IN ('handoff','summary','gap','sla')", name="ck_notifications_kind"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    target_staff_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcs_staff.id"), nullable=True
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)  # feishu/log/...
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    ref_handoff_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcs_handoffs.id"), nullable=True
    )
    # ref_gap_id：dcs_knowledge_gaps 表 Sprint-4 才建，本轮先 nullable、不加 FK
    ref_gap_id: Mapped[int | None] = mapped_column(nullable=True)


class KnowledgeGap(Base):
    """答不上的缺口问题记录。对应 dcs_knowledge_gaps。REQ-6。"""

    __tablename__ = "dcs_knowledge_gaps"
    __table_args__ = (
        CheckConstraint("status IN ('open','resolved')", name="ck_gaps_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    # 解决后回填的知识条目（P2 回写链路）；Sprint-4 建表留 nullable
    resolved_knowledge_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcs_knowledge_items.id"), nullable=True
    )


class Inquiry(Base):
    """定制询盘多轮收集状态。对应 dcs_inquiries。REQ-9（P2/Sprint-8）。"""

    __tablename__ = "dcs_inquiries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('collecting','completed','abandoned')", name="ck_inquiries_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="collecting")
    # 待确认维度（list[str]，如 ["尺寸","颜色","数量"]）；PG jsonb / SQLite JSON
    items_pending: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # 已收集 {维度: 值}（如 {"颜色":"蓝","数量":"100米"}）
    items_collected: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    current_item: Mapped[str | None] = mapped_column(String(32), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TopicHandoff(Base):
    """话题级转人工暂停状态。对应 dcs_topic_handoffs。REQ-10（P2/Sprint-12）。"""

    __tablename__ = "dcs_topic_handoffs"
    __table_args__ = (
        CheckConstraint(
            "handoff_state IN ('auto','handed_off')", name="ck_topic_handoffs_state"
        ),
        UniqueConstraint(
            "conversation_id", "topic_key", name="uq_topic_handoffs_conv_topic"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("dcs_conversations.id"), nullable=False
    )
    topic_key: Mapped[str] = mapped_column(String(128), nullable=False)  # 原型＝sender_external_id
    handoff_state: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
