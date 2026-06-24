"""口语化提醒生成 + 通知落库/发送。REQ-5。

对应 docs/design/routing-notification.md §2。口径＝像同事口头交代（含摘要、客户标识、
时间），非系统报表腔；模板优先，LLM 仅可作润色且须可回退（本 Sprint 用模板）。
"""
from sqlalchemy.orm import Session

from ...models import Notification
from .feishu import send_text


def build_handoff_body(
    *,
    staff_name: str | None,
    scenario: str,
    reason: str,
    customer: str,
    masked_contact: str | None,
) -> str:
    """生成口语化转交提醒。"""
    who = f"@{staff_name}" if staff_name else "相关同事"
    contact = f"，客户留了 {masked_contact}" if masked_contact else ""
    return (
        f"{who}，有一条{scenario}事项要跟进：{reason}{contact}。客户/群：{customer}。"
    )


def notify_handoff(
    db: Session,
    *,
    staff_id: int | None,
    body: str,
    ref_handoff_id: int,
    channel: str = "feishu",
) -> Notification:
    """落 dcs_notifications(kind=handoff)；若配了飞书 webhook 则发送。返回 notification。

    仅 db.add + db.flush，由调用方统一 commit。
    """
    notification = Notification(
        kind="handoff",
        target_staff_id=staff_id,
        channel=channel,
        body=body,
        ref_handoff_id=ref_handoff_id,
    )
    db.add(notification)
    db.flush()
    send_text(body)  # 未配置 webhook 时返回 None，静默跳过（通知已落库）
    return notification
