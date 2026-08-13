"""
celery连接和配置相关文件，且名字必须叫celery.py
文件名是 celery.py 时：路径写到包名即可（celery -A app.commons.celery_task worker --loglevel=info -P solo），Celery 会自动识别并加载包内的 celery.py
文件名是其他名字时：必须精确到模块（celery -A app.commons.celery_task.celery_config worker --loglevel=info -P solo），Celery 才能准确找到你自定义的配置文件。
"""
import os
from celery import Celery

# 初始化 Celery 实例
app = Celery(
    "demo",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/11"),
    backend=os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379/12"),
    include=[
        "app.commons.celery_task.user_task",  # 这边要使用完整路径
        "app.commons.celery_task.order_task",
        "app.commons.celery_task.crawl_task"
    ]
)
