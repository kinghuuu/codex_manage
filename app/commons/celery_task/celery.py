"""
celery连接和配置相关文件，且名字必须叫celery.py
文件名是 celery.py 时：路径写到包名即可（celery -A app.commons.celery_task worker --loglevel=info -P solo），Celery 会自动识别并加载包内的 celery.py
文件名是其他名字时：必须精确到模块（celery -A app.commons.celery_task.celery_config worker --loglevel=info -P solo），Celery 才能准确找到你自定义的配置文件。
"""
import os
from datetime import timedelta

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

# 加入定时任务
# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用 UTC 时间
app.conf.enable_utc = False

# 每隔5s，爬一次百度
app.conf.beat_schedule = {
    'my-timer-01': {
        'task': 'app.commons.celery_task.crawl_task.crawl_baidu',
        'schedule': timedelta(seconds=5),  # 每隔5s执行一次
        'args': ()  # 函数参数。 crawl_baidu没有参数，这里就不传
    }
}

"""
必须启动beat，让beat提交定时任务给 celery worker
所以需要启动两个进程：一个是负责干活的 Worker，另一个是负责发号施令的 Beat（调度器）
celery -A app.commons.celery_task worker --loglevel=info -P solo
celery -A app.commons.celery_task beat --loglevel=info
"""
