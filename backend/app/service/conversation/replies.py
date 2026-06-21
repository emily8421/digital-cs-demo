"""编排出站文案生成（纯函数）。REQ-2/6。

口径（design-conversation-engine §2）：命中作答限定在检索内容内、不编造；
未命中请留资 + 告知将请同事确认。模板优先，LLM 仅可作润色且须可回退（本 Sprint 用模板）。
"""


def build_answer(answer: str) -> str:
    """命中作答：直接回知识条目的标准答案（Sprint-4 不引入 LLM 改写）。"""
    return answer


def build_gap_reply() -> str:
    """未命中：请客户留资 + 告知将请同事确认（REQ-6 客户侧口径）。"""
    return (
        "这个问题我暂时还答不准，帮您请同事确认一下。"
        "方便留个联系方式吗？回复后会有专人跟进。"
    )
