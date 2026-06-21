"""飞书机器人 webhook 出站（design-routing-notification §2）。

仅当配置 FEISHU_WEBHOOK_URL 时实际发送；否则静默跳过（本机原型通知只落库）。
飞书 custom robot 文本消息格式：{"msg_type":"text","content":{"text": "..."}}。
"""
import httpx

from ...config import settings


def send_text(text: str) -> dict | None:
    """向飞书 custom robot 发一条文本消息；未配置 webhook 则返回 None（不发送）。"""
    url = settings.feishu_webhook_url
    if not url:
        return None
    resp = httpx.post(
        url, json={"msg_type": "text", "content": {"text": text}}, timeout=10.0
    )
    return {"status_code": resp.status_code, "body": resp.text}
