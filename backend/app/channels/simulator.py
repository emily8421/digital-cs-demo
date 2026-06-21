"""内置模拟器通道（design-channel-adapter §2·保底通道）。

入站：把 POST /api/v1/messages/simulate 的请求体转成 NormalizedMessage。
出站：Sprint-1 预留契约（暂未触发）——后续把回复/提醒写回 dcs_messages 即可，
无需任何外部平台，就能演示完整闭环。
"""
from datetime import datetime, timezone

from .base import NormalizedMessage


class SimulatorChannel:
    name = "simulator"

    def receive(self, payload: dict) -> NormalizedMessage:
        received_at = payload.get("received_at") or datetime.now(timezone.utc)
        # raw_payload 要能存进 JSON 列，故把 datetime 转成字符串
        raw = {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in payload.items()
        }
        return NormalizedMessage(
            external_group_id=payload["external_group_id"],
            sender_external_id=payload["sender_external_id"],
            content_type=payload.get("content_type") or "text",
            content_text=payload.get("content_text"),
            raw_payload=raw,
            received_at=received_at,
        )

    def send(self, target: str, body: str, kind: str) -> dict:
        """出站占位：实际写库由 service 层负责（需要 conversation_id）。"""
        return {"channel": self.name, "target": target, "body": body, "kind": kind}


# 单例：业务层直接 import 使用
simulator_channel = SimulatorChannel()
