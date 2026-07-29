from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.commons.settings import origins
from app.utils.exception import register_exceptions


def register_middlewares(app: FastAPI) -> None:
    """注册全局中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    """注册异常处理器"""
    register_exceptions(app)
