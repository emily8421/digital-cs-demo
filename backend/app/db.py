"""数据库引擎 / 会话 / Base。

原型期用 Base.metadata.create_all 建表（简单、对初学者友好）；
后续接入真实部署时换成 Alembic 迁移脚本（见 ai/project-rules.md §5.2）。
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

# expire_on_commit=False：commit 后对象属性仍可直接读，避免 DetachedInstance 报错
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖：每个请求一个 DB 会话，用完即关。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """建表（原型期）。导入 models 以确保表定义已注册。"""
    from . import models  # noqa: F401

    # 仅 PostgreSQL 启用 pgvector 扩展（SQLite 测试库无此语法，跳过）
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
