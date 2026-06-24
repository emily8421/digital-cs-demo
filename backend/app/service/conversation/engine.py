"""编排决策树：检索 → 命中作答 / 未命中缺口（请留资 + 转拍板人）。REQ-6。

对应 docs/design-conversation-engine.md §1/§2。

- act_on_search：纯编排副作用（给定检索结果），可单测（SQLite，不依赖 TEI/pgvector）。
- orchestrate：检索（knowledge_search，需 TEI）+ act_on_search，端到端用。
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ...models import Conversation, Handoff, KnowledgeGap, Message, TopicHandoff
from ..knowledge.search import KnowledgeHit, search as knowledge_search
from ..routing.notifier import build_handoff_body, notify_handoff
from ..routing.router import resolve_target
from .replies import build_answer, build_gap_reply, build_non_text_reply


@dataclass
class OrchestrationResult:
    """编排结果摘要（供 API 返回 / 日志）。"""

    hit: bool
    reply_text: str | None  # 客户侧出站文案（命中作答 / 未命中请留资）
    answer_source_id: int | None  # 命中的知识条目 id
    gap_id: int | None  # 缺口记录 id（未命中）
    handoff_id: int | None
    notification_id: int | None


def write_outbound(db: Session, conversation_id: int, channel: str, text: str) -> Message:
    """写一条出站消息（direction=outbound），模拟发回客户群（原型；真实通道经 OutboundChannel）。"""
    msg = Message(
        conversation_id=conversation_id,
        direction="outbound",
        channel=channel,
        sender_external_id="ai_assistant",
        content_type="text",
        content_text=text,
        received_at=datetime.now(timezone.utc),
    )
    db.add(msg)
    db.flush()
    return msg


def act_on_search(
    db: Session,
    conv: Conversation,
    question_text: str,
    channel: str,
    hit: bool,
    items: list[KnowledgeHit],
) -> OrchestrationResult:
    """给定检索结果，执行编排副作用（写 outbound / gap / handoff / notification）。

    命中→写 outbound 作答；未命中→写 gap(open) + outbound 请留资 + 转交拍板人 + 通知。
    仅 db.add + db.flush，由调用方统一 commit。
    """
    if hit and items:
        top = items[0]
        reply = build_answer(top.answer)
        write_outbound(db, conv.id, channel, reply)
        return OrchestrationResult(
            hit=True,
            reply_text=reply,
            answer_source_id=top.id,
            gap_id=None,
            handoff_id=None,
            notification_id=None,
        )

    # 未命中 → 缺口分支（REQ-6）
    gap = KnowledgeGap(conversation_id=conv.id, question_text=question_text)
    db.add(gap)
    db.flush()
    write_outbound(db, conv.id, channel, build_gap_reply())

    # 转交拍板人（unknown_question→owner）+ 通知
    target = resolve_target(db, "unknown_question")
    short_q = (question_text or "")[:50]
    handoff = Handoff(
        conversation_id=conv.id,
        scenario="unknown_question",
        target_staff_id=target.staff_id,
        reason=f"知识缺口：{short_q}",
        status="open",
    )
    db.add(handoff)
    db.flush()
    body = build_handoff_body(
        staff_name=target.staff_name,
        scenario="unknown_question",
        reason=f"客户问题未命中知识库：{short_q}",
        customer=conv.external_group_id,
        masked_contact=None,
    )
    notification = notify_handoff(
        db, staff_id=target.staff_id, body=body, ref_handoff_id=handoff.id
    )
    return OrchestrationResult(
        hit=False,
        reply_text=build_gap_reply(),
        gap_id=gap.id,
        handoff_id=handoff.id,
        notification_id=notification.id,
        answer_source_id=None,
    )


def orchestrate(
    db: Session,
    conv: Conversation,
    question_text: str,
    channel: str,
    embedder=None,
) -> OrchestrationResult:
    """检索 + 编排（端到端用，需 TEI/pgvector；单测请直接测 act_on_search 注入 fake 结果）。"""
    hit, items = knowledge_search(db, question_text, embedder=embedder)
    return act_on_search(db, conv, question_text, channel, hit, items)


def act_on_non_text(
    db: Session, conv: Conversation, content_type: str, channel: str
) -> OrchestrationResult:
    """非文字消息（REQ-12）：群内如实告知 + 提醒员工查看；不生成内容作答、不写 gap。"""
    reply = build_non_text_reply(content_type)
    write_outbound(db, conv.id, channel, reply)
    target = resolve_target(db, "unknown_question")
    body = build_handoff_body(
        staff_name=target.staff_name,
        scenario="non_text",
        reason=f"收到 {content_type} 消息，需人工查看",
        customer=conv.external_group_id,
        masked_contact=None,
    )
    notification = notify_handoff(
        db, staff_id=target.staff_id, body=body, ref_handoff_id=None
    )
    return OrchestrationResult(
        hit=False,
        reply_text=reply,
        answer_source_id=None,
        gap_id=None,
        handoff_id=None,
        notification_id=notification.id,
    )


def topic_handed_off(db: Session, conversation_id: int, topic_key: str) -> bool:
    """话题级暂停判定（REQ-10 话题级）：该会话该话题是否 handed_off。"""
    return (
        db.query(TopicHandoff)
        .filter_by(
            conversation_id=conversation_id,
            topic_key=topic_key,
            handoff_state="handed_off",
        )
        .first()
        is not None
    )
