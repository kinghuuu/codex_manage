"""
需要先启动celery任务：
celery -A app.commons.celery_task worker -l info -P solo
"""

import redis
import json
from app.commons.celery_task.crawl_task import crawl_baidu, crawl_csdnblog
from app.commons.celery_task.celery import app


def test_add_task():
    try:
        # 使用delay方法发送任务
        # 异步发送任务，立即返回一个 AsyncResult 对象
        async_result = crawl_baidu.delay()

        result = async_result.get(timeout=5)  # 等待任务完成，最多等待 5 秒
        print(f"任务: {async_result}")
        print(f"任务类型: {type(async_result)}")  # <class 'celery_task.result.AsyncResult'>
        print(f"任务ID: {async_result.id}")
        print(f"任务结果: {result}")

        r = redis.Redis(host='localhost', port=6379, db=12, decode_responses=True)
        current_key = f"celery-task-meta-{async_result.id}"

        redis_data = r.get(current_key)
        if redis_data:
            print(f"\n>>> Redis 原始数据: {redis_data}")
            data_dict = json.loads(redis_data)  # 解析一下看看里面的内容
            print(f">>> 状态: {data_dict.get('status')}")
            print(f">>> 结果: {data_dict.get('result')}")
        else:
            print("Redis 中未找到该任务数据（可能已过期）")
    finally:
        del async_result  # 显式删除 async_result 对象，触发清理
        app.close()  # 清理连接。 这里不会停止 Worker，只是关闭客户端连接。


if __name__ == '__main__':
    test_add_task()
