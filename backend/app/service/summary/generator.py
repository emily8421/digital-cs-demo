"""定时小结生成（REQ-7）。

聚合消息量/类型 + 需跟进清单 → 口语化经营者小结，落 dcs_notifications(kind=summary)。
对应 docs/design/routing-notification.md §2。口径＝像经营者口头汇报「该关注什么」，非系统报表腔。
"""
from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...models import Handoff, Message, Notification, Staff

_TYPE_LABEL = {"text": "文字", "voice": "语音", "image": "图片", "video": "视频"}
_SCENARIO_LABEL = {
    "presale": "售前",
    "unknown_question": "待确认问题",
    "order": "订单",
    "aftersale": "售后",
    "non_text": "非文字需查看",
}


@dataclass
class DailySummary:
    notification_id: int
    summary: str


def generate_daily_summary(db: Session) -> DailySummary:
    """聚合全部入站消息 + open 转交 → 经营者小结，落 dcs_notifications(kind=summary)。

    本机原型聚合全部消息；生产应按 window（当日起止）过滤 received_at。
    """
    total = db.query(Message).filter_by(direction="inbound").count()
    type_rows = (
        db.query(Message.content_type, func.count(Message.id))
        .filter_by(direction="inbound")
        .group_by(Message.content_type)
        .all()
    )
    type_desc = "、".join(f"{_TYPE_LABEL.get(t, t)}{c}条" for t, c in type_rows) or "暂无"

    handoffs = db.query(Handoff).filter_by(status="open").all()
    followups = []
    for h in handoffs:
        staff = db.get(Staff, h.target_staff_id) if h.target_staff_id else None
        who = staff.name if staff else "待分配"
        followups.append(f"{_SCENARIO_LABEL.get(h.scenario, h.scenario)}({who})")
    followup_desc = "、".join(followups) if followups else "无"

    if total == 0:
        summary = "今天还没有客户消息，有新消息我会及时处理并汇报。"
    else:
        summary = (
            f"今天共 {total} 条客户消息（{type_desc}），多数已自动回复；"
            f"其中 {len(handoffs)} 条需跟进：{followup_desc}，均已通知对应同事。"
        )

    owner = (
        db.query(Staff)
        .filter(Staff.role == "owner", Staff.active.is_(True))
        .order_by(Staff.id)
        .first()
    )
    notification = Notification(
        kind="summary",
        target_staff_id=owner.id if owner else None,
        channel="feishu",
        body=summary,
    )
    db.add(notification)
    db.flush()
    return DailySummary(notification_id=notification.id, summary=summary)
