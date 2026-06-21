"""通道适配层契约（design-channel-adapter §1）。

设计核心：业务层（编排/service）只依赖这里的 NormalizedMessage 与接口，
不感知是模拟器、企业微信还是别的平台——换通道不用动业务代码。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class NormalizedMessage:
    """归一化入站消息（任何通道进来都变成这个结构）。"""

    external_group_id: str
    sender_external_id: str
    content_type: str  # text / voice / image / video / other
    content_text: str | None
    raw_payload: dict | None  # 平台原始报文（归一化前留存）
    received_at: datetime


class InboundChannel(Protocol):
    """入站适配器：把平台报文转成 NormalizedMessage。"""

    name: str

    def receive(self, payload: dict) -> NormalizedMessage: ...


class OutboundChannel(Protocol):
    """出站适配器：把回复/提醒发回客户群或员工（Sprint-1 仅占位契约，未触发）。"""

    name: str

    def send(self, target: str, body: str, kind: str) -> dict: ...
