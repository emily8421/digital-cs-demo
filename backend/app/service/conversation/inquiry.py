"""定制询盘多轮引导（REQ-9，Sprint-8）。对应 docs/design-conversation-engine.md §3.1。

纯规则识别 + 拆项 + 状态机 + 摘要；**不引 LLM**（守 §2 可控性约束）。

- detect_custom_inquiry / build_summary：纯逻辑，可单测（SQLite，无 TEI/pgvector）。
- start_inquiry / act_on_inquiry_reply：db 副作用（写 inquiry / outbound / handoff / notification）。

原型简化：假设客户**逐项配合**回答当前维度（跑题/答非所问的「不匹配重申」留优化，
见 design §3.1 未应答兜底）；超时留 Sprint-11 SLA。
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ...models import Conversation, Handoff, Inquiry
from ..routing.notifier import build_handoff_body, notify_handoff
from ..routing.router import resolve_target
from .engine import OrchestrationResult, _write_outbound

# 定制触发词（含其一即视为「定制」语境）
_CUSTOM_TRIGGERS = ("定制", "定做", "订做", "我要做", "想定做", "需要定做", "想定制", "想要定制")

# 维度关键词 → 维度名（抽取待确认项用；按灯饰业务可调）
_DIM_KEYWORDS: dict[str, list[str]] = {
    "尺寸": ["尺寸", "大小", "长", "长度", "宽", "高"],
    "颜色": ["颜色", "什么色", "色", "红", "蓝", "绿", "黄", "白", "黑", "暖白", "正白", "冷白", "橙", "紫", "粉", "灰"],
    "数量": ["数量", "几个", "多少", "米", "个", "条", "根", "卷", "套"],
    "材质": ["材质", "材料"],
    "Logo": ["logo", "标志", "印字", "印花", "印logo", "印Logo", "LOGO"],
    "包装": ["包装", "盒装", "袋装"],
    "交期": ["交期", "交货", "几天", "多久", "到货"],
}

# 跳过指令（结束收集，转已收集项）
_SKIP_WORDS = ("跳过", "没有了", "没了", "就这些", "没要求", "不用了", "其他没")

# 转交场景（已有路由 presale→sales；定制询盘核价走售前，可按业务调路由）
_HANDOFF_SCENARIO = "presale"


# 客户未陈述具体规格时，默认逐项确认的核心维度（按灯饰定制可调）
_DEFAULT_DIMS = ["颜色", "数量", "Logo", "交期"]


def detect_custom_inquiry(text: str) -> list[str] | None:
    """文本是否定制询盘；是则返回待确认维度列表，否则 None。

    规则：含定制触发词即识别；维度 = 从文本抽到的规格词维度，抽不到则用默认核心维度。
    （原型：不抽值预填，系统主导逐项让客户确认；智能预填留优化，见 design §3.1。）
    """
    if not text:
        return None
    if not any(t in text for t in _CUSTOM_TRIGGERS):
        return None
    found = [
        dim for dim, kws in _DIM_KEYWORDS.items() if any(k.lower() in text.lower() for k in kws)
    ]
    return found if found else list(_DEFAULT_DIMS)


def build_summary(collected: dict) -> str:
    """把已收集 {维度: 值} 整理为可核价摘要文本。"""
    if not collected:
        return "（未收集到具体规格）"
    return " / ".join(f"{k}={v}" for k, v in collected.items())


def get_active_inquiry(db: Session, conversation_id: int) -> Inquiry | None:
    """查某会话进行中(collecting)的询盘；原型假设串行，取最近一条。"""
    return (
        db.query(Inquiry)
        .filter_by(conversation_id=conversation_id, status="collecting")
        .order_by(Inquiry.id.desc())
        .first()
    )


def _confirm_prompt(item: str) -> str:
    return f"好的，定制询盘帮您逐项确认。请问【{item}】是？"


def start_inquiry(
    db: Session, conv: Conversation, items: list[str], channel: str
) -> OrchestrationResult:
    """新建询盘（collecting）+ 出站确认第一项。"""
    inquiry = Inquiry(
        conversation_id=conv.id,
        status="collecting",
        items_pending=list(items),
        items_collected={},
        current_item=items[0],
    )
    db.add(inquiry)
    db.flush()
    prompt = _confirm_prompt(items[0])
    _write_outbound(db, conv.id, channel, prompt)
    return OrchestrationResult(
        hit=False,
        reply_text=prompt,
        answer_source_id=None,
        gap_id=None,
        handoff_id=None,
        notification_id=None,
    )


def act_on_inquiry_reply(
    db: Session, inquiry: Inquiry, reply_text: str, channel: str
) -> OrchestrationResult:
    """处理多轮中的客户回复：跳过 / 收集当前项 → 确认下一项 或 全部完成转交。"""
    pending = list(inquiry.items_pending or [])
    collected = dict(inquiry.items_collected or {})
    cur = inquiry.current_item

    skipped = any(w in (reply_text or "") for w in _SKIP_WORDS)
    if not skipped and cur:
        collected[cur] = (reply_text or "").strip()
    if cur and cur in pending:
        pending.remove(cur)

    inquiry.items_collected = collected
    inquiry.updated_at = datetime.now(timezone.utc)

    if pending:
        # 还有项 → 确认下一项
        nxt = pending[0]
        inquiry.items_pending = pending
        inquiry.current_item = nxt
        prompt = _confirm_prompt(nxt)
        _write_outbound(db, inquiry.conversation_id, channel, prompt)
        return OrchestrationResult(
            hit=False,
            reply_text=prompt,
            answer_source_id=None,
            gap_id=None,
            handoff_id=None,
            notification_id=None,
        )

    # 全部收集完 → 生成摘要 + 转交（handoff + 通知）+ inquiry completed
    inquiry.items_pending = []
    inquiry.current_item = None
    inquiry.status = "completed"
    inquiry.completed_at = datetime.now(timezone.utc)
    summary = build_summary(collected)
    inquiry.summary = summary

    conv = db.query(Conversation).filter_by(id=inquiry.conversation_id).first()
    target = resolve_target(db, _HANDOFF_SCENARIO)
    handoff = Handoff(
        conversation_id=inquiry.conversation_id,
        scenario=_HANDOFF_SCENARIO,
        target_staff_id=target.staff_id if target else None,
        reason=f"定制询盘：{summary}",
        status="open",
    )
    db.add(handoff)
    db.flush()
    body = build_handoff_body(
        staff_name=target.staff_name if target else "（待分配）",
        scenario=_HANDOFF_SCENARIO,
        reason=f"定制询盘已收集，请核价：{summary}",
        customer=conv.external_group_id if conv else None,
        masked_contact=None,
    )
    notification = notify_handoff(
        db,
        staff_id=(target.staff_id if target else None),
        body=body,
        ref_handoff_id=handoff.id,
    )
    done_msg = f"收到，已为您整理：{summary}，转给同事核价，稍后回复您 🙂"
    _write_outbound(db, inquiry.conversation_id, channel, done_msg)
    return OrchestrationResult(
        hit=False,
        reply_text=done_msg,
        answer_source_id=None,
        gap_id=None,
        handoff_id=handoff.id,
        notification_id=notification.id,
    )
