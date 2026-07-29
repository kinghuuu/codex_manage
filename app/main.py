"""应用入口: 初始化 FastAPI 实例、挂载路由与中间件"""
from fastapi import FastAPI

from app.modules.config.views import auth, user
from app.modules.news.views import news, history, favorite
from app.utils import test_websocket, test_email
from app.utils.database import Base, engine, dispose_engine
from app.utils.cache_conf import redis_client
from app.utils.logger import bind_logger
from app.utils.middleware import register_middlewares
from sqlalchemy import text


async def my_init(app: FastAPI):
    # 启动时执行
    print("my_init 启动了")
    yield print("my_init 启动完成")
    # 关闭时执行
    print("my_init 关闭了")


app = FastAPI(
    title="Codex Manage",
    lifespan=my_init,
)

logger = bind_logger(app)  # 绑定 logger

register_middlewares(app)  # 注册中间件 & 异常处理


@app.on_event("startup")
async def startup_event() -> None:
    """启动时检查 Redis 和 PostgreSQL 是否可用，然后创建数据库表。"""
    # 1. 检查 Redis
    try:
        await redis_client.ping()
        print("[startup] Redis 连接成功")
    except Exception as e:
        raise RuntimeError(f"Redis 不可用，请先启动 Docker Redis 容器: {e}")

    # 2. 检查 PostgreSQL
    try:
        async with engine.connect() as conn:
            await conn.execute(
                text("SELECT 1")
            )
        print("[startup] PostgreSQL 连接成功")
    except Exception as e:
        await dispose_engine()
        raise RuntimeError(f"PostgreSQL 不可用，请先启动 Docker PostgreSQL 容器: {e}")

    # 3. 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[startup] 数据库表创建完成")


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(news.router)
app.include_router(history.router)
app.include_router(favorite.router)

app.include_router(test_websocket.router)
app.include_router(test_email.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test")
async def test():
    return {"test": "123"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010,
    )


