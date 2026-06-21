"""对话编排（design-conversation-engine）。

Sprint-1：解析会话 + 入站消息入库。
Sprint-3：文本消息顺带抽取留资（REQ-4）。
后续 Sprint 在此扩展分支：检索作答 / 缺口 / 转交 / 转人工暂停 / 非文字处理……
（都挂在 handle_inbound 里，保持“一条消息进来 → 一处编排”的单一入口。）
"""
from sqlalchemy.orm import Session

from ..channels.base import NormalizedMessage
from ..models import Conversation, Message
from .leads.service import capture_lead


def handle_inbound(
    db: Session, msg: NormalizedMessage, channel_name: str = "simulator"
) -> tuple[int, int, int | None]:
    """处理一条归一化入站消息：确保会话存在 + 写消息；文本消息顺带抽取留资（REQ-4）。

    返回 (message_id, conversation_id, lead_id)；lead_id 为 None 表示无留资。
    """
    conv = (
        db.query(Conversation)
        .filter_by(external_group_id=msg.external_group_id)
        .first()
    )
    if conv is None:
        conv = Conversation(
            external_group_id=msg.external_group_id, last_active_at=msg.received_at
        )
        db.add(conv)
        db.flush()  # 拿到 conv.id，先不 commit
    conv.last_active_at = msg.received_at

    message = Message(
        conversation_id=conv.id,
        direction="inbound",
        channel=channel_name,
        sender_external_id=msg.sender_external_id,
        content_type=msg.content_type,
        content_text=msg.content_text,
        raw_payload=msg.raw_payload,
        received_at=msg.received_at,
    )
    db.add(message)
    db.flush()  # 拿到 message.id，供留资 note 引用

    # 留资抽取（REQ-4）：仅文本消息尝试抽手机号；无则不产生记录
    lead = (
        capture_lead(db, conv.id, msg.content_text, note=f"来自消息#{message.id}")
        if msg.content_type == "text"
        else None
    )

    db.commit()
    db.refresh(message)
    return message.id, conv.id, (lead.id if lead else None)
