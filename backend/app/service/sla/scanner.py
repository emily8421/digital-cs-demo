"""响应时效 SLA 监控（REQ-14，Sprint-11）。对应 docs/design/routing-notification.md §3.1。

扫描「客户消息 → 首次应答」间隔，对 > 阈值未回复者提示。
计时口径：每会话最后一条客户消息(inbound)，若同会话无 received_at 更晚的
outbound（AI 应答）且距今 > 阈值 → 超时未答。
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ...config import settings
from ...models import Conversation, Message, Notification, Staff


@dataclass
class OverdueItem:
    conversation_id: int
    group: str
    message_id: int
    overdue_minutes: int


@dataclass
class ScanResult:
    overdues: list[OverdueItem]
    count: int
    notification_id: int | None
    prompt: str | None


def scan_sla(db: Session, threshold_minutes: float | None = None) -> ScanResult:
    """扫描超时未答的客户消息；有超时则写 Notification(kind=sla) 提示经营者。"""
    if threshold_minutes is None:
        threshold_minutes = settings.sla_threshold_minutes
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=threshold_minutes)

    overdues: list[OverdueItem] = []
    for conv in db.query(Conversation).all():
        last_in = (
            db.query(Message)
            .filter_by(conversation_id=conv.id, direction="inbound")
            .order_by(Message.received_at.desc())
            .first()
        )
        if last_in is None:
            continue
        # 同会话是否有更晚的 outbound（AI 应答）→ 有则已答，不计
        answered = (
            db.query(Message)
            .filter_by(conversation_id=conv.id, direction="outbound")
            .filter(Message.received_at > last_in.received_at)
            .first()
        )
        if answered:
            continue
        recv = last_in.received_at
        if recv.tzinfo is None:
            recv = recv.replace(tzinfo=timezone.utc)  # SQLite 存 naive → 按 UTC 对齐
        if recv < cutoff:
            mins = int((now - recv).total_seconds() // 60)
            overdues.append(
                OverdueItem(conv.id, conv.external_group_id, last_in.id, mins)
            )

    notification_id = None
    prompt = None
    if overdues:
        detail = "、".join(f"{o.group}({o.overdue_minutes}分钟)" for o in overdues)
        prompt = f"时效提醒：{len(overdues)} 条客户消息未回复：{detail}，请关注。"
        owner = (
            db.query(Staff)
            .filter(Staff.role == "owner", Staff.active.is_(True))
            .order_by(Staff.id)
            .first()
        )
        try:
            n = Notification(
                kind="sla",
                target_staff_id=owner.id if owner else None,
                channel="feishu",
                body=prompt,
            )
            db.add(n)
            db.flush()
            notification_id = n.id
        except Exception:  # noqa: BLE001  # notifications 表 CHECK 不含 sla（PG 旧表）→ 降级，只返回列表
            db.rollback()
    return ScanResult(overdues, len(overdues), notification_id, prompt)
