"""定制询盘多轮引导（REQ-9，Sprint-8）。对应 docs/design-conversation-engine.md §3.1。

纯规则识别 + 拆项（抽维度+抽值预填）+ 状态机 + 摘要；**不引 LLM**（守 §2 可控性）。

- detect_custom_inquiry / build_summary：纯逻辑，可单测（SQLite，无 TEI/pgvector）。
- start_inquiry / act_on_inquiry_reply：db 副作用（写 inquiry / outbound / handoff / notification）。

抽值预填：客户首条陈述的规格（蓝色/100米/要logo/7天）抽值预填 collected，
系统只追问未陈述的维度（pending），不重复问；未陈述规格时用默认核心维度。
"""
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ...models import Conversation, Handoff, Inquiry
from ..routing.notifier import build_handoff_body, notify_handoff
from ..routing.router import resolve_target
from .engine import OrchestrationResult, _write_outbound

# 定制触发词（含其一即视为「定制」语境）
_CUSTOM_TRIGGERS = ("定制", "定做", "订做", "我要做", "想定做", "需要定做", "想定制", "想要定制")

# 维度关键词 → 维度名（识别客户陈述的维度；按灯饰业务可调）
_DIM_KEYWORDS: dict[str, list[str]] = {
    "尺寸": ["尺寸", "大小", "长", "长度", "宽", "高"],
    "颜色": ["颜色", "什么色", "色", "红", "蓝", "绿", "黄", "白", "黑", "暖白", "正白", "冷白", "橙", "紫", "粉", "灰"],
    "数量": ["数量", "几个", "多少", "米", "个", "条", "根", "卷", "套"],
    "材质": ["材质", "材料"],
    "Logo": ["logo", "标志", "印字", "印花", "LOGO"],
    "包装": ["包装", "盒装", "袋装"],
    "交期": ["交期", "交货", "几天", "多久", "到货"],
}

# 抽值正则（能抽到值就预填 collected，不再追问该维度）
_VALUE_PATTERNS: dict[str, str] = {
    "颜色": r"(暖白|正白|冷白|红|蓝|绿|黄|白|黑|橙|紫|粉|灰)色?",
    "数量": r"\d+(?:\.\d+)?\s*(?:米|个|条|根|卷|套|pcs)",
    "Logo": r"(?:不要|不需要|没有|不带|不加|要|带|加|印|需要)\s*logo",
    "交期": r"\d+\s*(?:天|日|周)",
}

# 客户未陈述具体规格时，默认逐项确认的核心维度
_DEFAULT_DIMS = ["颜色", "数量", "Logo", "交期"]

# 跳过指令（跳过当前项，转下一项或完成）
_SKIP_WORDS = ("跳过", "没有了", "没了", "就这些", "没要求", "不用了", "其他没")

# 转交场景（已有路由 presale→sales；定制询盘核价走售前，可按业务调路由）
_HANDOFF_SCENARIO = "presale"


def detect_custom_inquiry(text: str) -> tuple[dict, list] | None:
    """识别定制询盘；返回 (collected, pending)，否则 None。

    - collected：从文本抽到值的维度（颜色/数量/Logo/交期，正则预填，值为客户原话片段）
    - pending：默认核心维度里没抽到值的 + 客户陈述的其他维度（尺寸/材质/包装，无抽值正则）
    """
    if not text or not any(t in text for t in _CUSTOM_TRIGGERS):
        return None
    tl = text.lower()
    collected: dict[str, str] = {}
    for dim, pat in _VALUE_PATTERNS.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            collected[dim] = m.group(0)
    stated = [dim for dim, kws in _DIM_KEYWORDS.items() if any(k.lower() in tl for k in kws)]
    pending: list[str] = [d for d in _DEFAULT_DIMS if d not in collected]
    for d in stated:
        if d not in collected and d not in pending:
            pending.append(d)
    return collected, pending


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
    return f"请问【{item}】是？"


def _complete_inquiry(db: Session, inquiry: Inquiry, channel: str) -> OrchestrationResult:
    """询盘收集完：生成可核价摘要 + 转交（handoff + 通知）+ inquiry=completed。"""
    inquiry.status = "completed"
    inquiry.current_item = None
    inquiry.items_pending = []
    inquiry.completed_at = datetime.now(timezone.utc)
    summary = build_summary(inquiry.items_collected or {})
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


def start_inquiry(
    db: Session, conv: Conversation, collected: dict, pending: list, channel: str
) -> OrchestrationResult:
    """新建询盘（预填 collected）+ 出站：ack 已收到 + 问第一项；全预填则直接完成。"""
    inquiry = Inquiry(
        conversation_id=conv.id,
        status="collecting",
        items_pending=list(pending),
        items_collected=dict(collected),
        current_item=pending[0] if pending else None,
    )
    db.add(inquiry)
    db.flush()
    if not pending:
        return _complete_inquiry(db, inquiry, channel)
    ack = (
        f"收到您的需求：{build_summary(collected)}。还需确认几项。"
        if collected
        else "好的，定制询盘帮您逐项确认。"
    )
    prompt = ack + _confirm_prompt(pending[0])
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
    """多轮接续：跳过/收集当前项 → 问下一项 或 全部完成转交。"""
    pending = list(inquiry.items_pending or [])
    collected = dict(inquiry.items_collected or {})
    cur = inquiry.current_item

    skipped = any(w in (reply_text or "") for w in _SKIP_WORDS)
    if cur:
        # 跳过也记入 collected（标「（跳过）」），让摘要可见核价人知晓该维度未提供
        collected[cur] = "（跳过）" if skipped else (reply_text or "").strip()
    if cur and cur in pending:
        pending.remove(cur)

    inquiry.items_collected = collected
    inquiry.updated_at = datetime.now(timezone.utc)

    if pending:
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
    return _complete_inquiry(db, inquiry, channel)
