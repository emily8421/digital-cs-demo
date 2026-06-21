"""配置：从 .env / 环境变量读取，带本机默认值。初学者友好——不配也能跑。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 本机默认指向 docker compose 起的 PG（psycopg3 驱动）
    database_url: str = "postgresql+psycopg://dcs:dcs@localhost:5432/dcs"
    app_host: str = "127.0.0.1"
    app_port: int = 8000


settings = Settings()
