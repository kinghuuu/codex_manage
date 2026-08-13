"""
项目用到的配置文件
"""
from pydantic_settings import BaseSettings

# 解决跨域，允许的来源
origins = [
    "http://localhost:8123",  # 配置开发环境前端域名和端口
    "https://your-frontend-domain.com:8888",  # 配置生产环境的前端域名和端口
]


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
