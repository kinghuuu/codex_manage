"""Async database configuration for PostgreSQL."""

from collections.abc import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "codex_manage")

ASYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# 创建异步数据库引擎，用于管理数据库连接池
async_engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选，输出SQL日志
    future=True,
    pool_size=10,  # 可选，设置数据库连接池中保持的持久连接数
    max_overflow=20,  # 可选，设置数据库连接池中允许创建的额外连接数，那最大连接数 = pool_size + max_overflow
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

engine = async_engine

# 创建异步会话工厂，用于生成数据库会话对象
async_session_maker = async_sessionmaker(
    bind=async_engine,  # 绑定到之前创建的异步引擎
    class_=AsyncSession,  # 指定会话类为 AsyncSession
    expire_on_commit=False,  # 提交后不使对象属性过期，保持数据可访问
    autoflush=False,
    autocommit=False,
)


# 定义FastAPI依赖注入函数，用于获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting an async database session."""
    async with async_session_maker() as session:
        yield session


async def dispose_engine() -> None:
    """Close all engine connections."""
    await async_engine.dispose()
