from app.commons.celery_task.celery import app
from celery.result import AsyncResult


id = ''  # 任务ID
if __name__ == '__main__':
    result = AsyncResult(id=id, app=app)
    if result.successful():
        print(result.get())
    elif result.failed():
        print(result.traceback)
    elif result.status == 'PENDING':
        print('任务正在等待执行...')
    elif result.status == 'RETRY':
        print('任务正在重新执行...')
    elif result.status == 'REVOKED':
        print('任务被撤销...')
