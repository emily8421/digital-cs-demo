"""AI 身份披露（REQ-11，Sprint-9）。对应 docs/design-conversation-engine.md §3.2。

被动披露：被问「是不是AI/机器人」时，按既定口径自然承认身份，不喧宾夺主。
纯规则识别（不引 LLM）；单轮（问→答）；不主动披露、不触发缺口/转交。
"""
from sqlalchemy.orm import Session

from ...models import Conversation
from .engine import OrchestrationResult, write_outbound

# 身份询问触发模式（明确问「你是不是AI/机器人/真人」类；弱词如单独「机器人」不收，防误判）
_IDENTITY_PATTERNS = (
    "你是机器人", "你是 ai", "你是ai", "你是人工智能", "你是真人", "你是人吗",
    "你是假的", "你是程序", "你是自动回复", "你是客服机器人", "你是机器",
    "是不是机器人", "是不是ai", "是不是人工智能", "是不是真人", "是不是人",
    "你是真人还是", "你是机器还是", "你是人工还是",
)

# 既定披露话术（承认身份 + 角色 + 回归服务，不喧宾夺主）
_DISCLOSURE = (
    "我是小辰，汇辰灯饰的 AI 客服助理 🤖 能帮您查产品参数、记需求转同事跟进。"
    "有什么可以帮您的？"
)


def detect_identity_question(text: str) -> bool:
    """是否在问 AI 身份（被动触发）。"""
    if not text:
        return False
    tl = text.lower()
    return any(p in tl for p in _IDENTITY_PATTERNS)


def build_identity_reply() -> str:
    return _DISCLOSURE


def act_on_identity(db: Session, conv: Conversation, channel: str) -> OrchestrationResult:
    """身份披露：写 outbound 既定话术；单轮，不触多轮/检索/缺口/转交。"""
    reply = build_identity_reply()
    write_outbound(db, conv.id, channel, reply)
    return OrchestrationResult(
        hit=False,
        reply_text=reply,
        answer_source_id=None,
        gap_id=None,
        handoff_id=None,
        notification_id=None,
    )
