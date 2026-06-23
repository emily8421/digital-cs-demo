"""配置：从 .env / 环境变量读取，带本机默认值。初学者友好——不配也能跑。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 本机默认指向 docker compose 起的 PG（psycopg3 驱动）
    database_url: str = "postgresql+psycopg://dcs:dcs@localhost:15432/dcs"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    # 知识库检索（Sprint-2）：embedding 由 docker 的 TEI 服务提供，宿主 httpx 调用
    embedding_service_url: str = "http://localhost:18080"  # text-embeddings-inference 服务
    embedding_model: str = "BAAI/bge-small-zh-v1.5"  # TEI 加载的 BGE 中文模型（512 维，配于 docker-compose）
    knowledge_score_threshold: float = 0.5  # 命中阈值（cosine 相似度）；按种子相似度分布初定（相关≥0.50、无关≤0.46），待真实语料复核，见 design-knowledge-base §2
    # 转交通知出站（Sprint-3）：飞书 custom robot webhook；空则通知只落库不发送（本机原型）
    feishu_webhook_url: str = ""
    # 响应时效 SLA 阈值（REQ-14）：客户消息→首次应答 超时分钟数（愿景口径 30）
    sla_threshold_minutes: float = 30.0


settings = Settings()
