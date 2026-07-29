"""应用入口: 初始化 FastAPI 实例、挂载路由与中间件"""
from fastapi import FastAPI

from app.modules.config.views import auth, user
from app.modules.news.views import news, history, favorite
from app.utils import test_websocket, test_email
from app.utils.datebase import Base, engine
from app.utils.logger import bind_logger
from app.utils.middleware import register_middlewares


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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
