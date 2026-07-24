"""
应用入口: 初始化 FastAPI 实例、挂载路由与中间件
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.commons.settings import origins
from app.modules.config.views import auth, user
from app.utils.datebase import Base, engine
from app.utils.exception import register_exceptions
from app.utils.logger import bind_logger

app = FastAPI(
    title="Codex Manage",
)

logger = bind_logger(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exceptions(app)


@app.on_event("startup")
async def startup_event() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(user.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010
    )
