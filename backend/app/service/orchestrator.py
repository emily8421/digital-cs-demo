"""对话编排（design-conversation-engine）。

Sprint-1：解析会话 + 入站消息入库。
Sprint-3：文本消息顺带抽取留资（REQ-4）。
后续 Sprint 在此扩展分支：检索作答 / 缺口 / 转交 / 转人工暂停 / 非文字处理……
（都挂在 handle_inbound 里，保持“一条消息进来 → 一处编排”的单一入口。）
"""
from sqlalchemy.orm import Session

from ..channels.base import NormalizedMessage
from ..models import Conversation, Message
from .conversation.engine import OrchestrationResult, act_on_non_text, orchestrate
from .conversation.inquiry import (
    act_on_inquiry_reply,
    detect_custom_inquiry,
    get_active_inquiry,
    start_inquiry,
)
from .leads.service import capture_lead


def handle_inbound(
    db: Session, msg: NormalizedMessage, channel_name: str = "simulator"
) -> tuple[int, int, int | None, OrchestrationResult | None]:
    """处理一条归一化入站消息：入库 + 留资抽取（REQ-4）+ 编排（REQ-6 检索作答/缺口）。

    返回 (message_id, conversation_id, lead_id, orchestration)；orchestration 为 None
    表示未做编排（非文本消息，或检索不可用被跳过——如 SQLite 测试无 TEI/pgvector）。
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

    # 编排（REQ-6/10/12）：会话级暂停 → 非文字如实告知 → 文本检索作答/缺口。
    # 检索依赖 TEI+pgvector，不可用时（如 SQLite 测试环境）优雅跳过，不阻塞入库。
    orchestration: OrchestrationResult | None = None
    if conv.handoff_state == "handed_off":
        pass  # REQ-10：已转人工，暂停所有自动编排（仅记录消息）
    elif msg.content_type != "text":
        try:  # REQ-12：非文字如实告知 + 提醒员工查看
            orchestration = act_on_non_text(db, conv, msg.content_type, channel_name)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 非文字处理跳过：{e}")
    elif msg.content_text:
        try:  # REQ-9 多轮引导优先 → REQ-6 检索作答 / 未命中缺口
            active = get_active_inquiry(db, conv.id)
            if active:  # 多轮接续：匹配客户回复到当前项
                orchestration = act_on_inquiry_reply(db, active, msg.content_text, channel_name)
            else:
                items = detect_custom_inquiry(msg.content_text)
                if items:  # 新定制询盘：建 inquiry + 首轮确认
                    orchestration = start_inquiry(db, conv, items, channel_name)
                else:  # 普通文本：检索作答 / 未命中缺口
                    orchestration = orchestrate(db, conv, msg.content_text, channel_name)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 编排跳过（检索不可用？）：{e}")

    db.commit()
    db.refresh(message)
    return message.id, conv.id, (lead.id if lead else None), orchestration
