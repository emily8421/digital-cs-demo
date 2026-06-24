"""留资识别：从文本抽取手机号并脱敏（REQ-4）。

纯函数，无 DB / 外部依赖，便于单元测试。
"""
import re

# 中国大陆手机号：1[3-9] 开头 + 9 位数字（共 11 位）；前后不能是数字（避免从长串截出假号）
_PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")


def find_phone(text: str | None) -> str | None:
    """从文本抽取第一个合规手机号；无则 None。"""
    if not text:
        return None
    m = _PHONE_RE.search(text)
    return m.group(0) if m else None


def mask_phone(phone: str) -> str:
    """脱敏：前 3 后 4，中间 ****（如 138****6677）。"""
    if len(phone) != 11:
        return phone  # 非标准长度原样返回（find_phone 已保证 11 位，此处兜底）
    return f"{phone[:3]}****{phone[7:]}"


def mask_phones_in_text(text: str | None) -> str | None:
    """脱敏文本中所有手机号（入库前合规：避免明文手机号留存 messages 表）。"""
    if not text:
        return text
    return _PHONE_RE.sub(lambda m: mask_phone(m.group(0)), text)


def mask_phones_in_payload(payload: dict | None) -> dict | None:
    """脱敏 raw_payload 顶层 str 值中的手机号（平台原始报文同需合规）。"""
    if not payload:
        return payload
    return {
        k: mask_phones_in_text(v) if isinstance(v, str) else v for k, v in payload.items()
    }
