"""
全局日志配置
"""
import logging
import os
from logging.config import dictConfig

from fastapi import FastAPI

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOGGER_NAME = "codex_manage"


def get_logger(name: str | None = None) -> logging.Logger:
    """
    获取项目 logger；业务模块建议传入 __name__，便于定位日志来源。
    """
    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def setup_logging(log_level: str = DEFAULT_LOG_LEVEL) -> logging.Logger:
    """
    初始化全局 logging 配置，并返回项目主 logger。
    """
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
            "loggers": {
                LOGGER_NAME: {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": log_level,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
            },
        }
    )
    return get_logger()


def bind_logger(app: FastAPI, logger: logging.Logger | None = None) -> logging.Logger:
    """
    将项目 logger 绑定到 FastAPI 实例，便于应用生命周期或中间件使用。
    """
    app.state.logger = logger or setup_logging()
    return app.state.logger
