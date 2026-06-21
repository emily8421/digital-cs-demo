"""知识库 embedding（本地 BGE 服务）。

部署：docker compose 起 text-embeddings-inference（TEI），加载 bge-small-zh-v1.5
（512 维，TEI 输出已归一化）。宿主用 httpx 调用，**不依赖 torch**——Python 3.14 + Windows
下进程内 torch/onnx 的原生 DLL 加载失败，改由容器内 Linux 跑 TEI（见 docs/05-tech-spec.md、
docs/context-and-constraints.md §3）。

测试可通过 Embedder 协议注入 fake（见 tests/test_knowledge.py）。
"""
from typing import Protocol

import httpx

from ...config import settings


class Embedder(Protocol):
    """把文本变成定长向量（抽象，便于测试注入 fake）。"""

    def embed(self, text: str) -> list[float]: ...


def embed(text: str) -> list[float]:
    """调本地 TEI 服务生成 embedding。

    TEI `POST /embed {"inputs": text}` 返回 `[[...]]`（外层 list，每元素一条向量）；
    与 pgvector cosine 距离（<=>）配合，score = 1 - distance。
    """
    resp = httpx.post(
        f"{settings.embedding_service_url}/embed",
        json={"inputs": text},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()[0]
