import time
from .celery import app  # .表示当前路径, 当前路径下的celery文件


@app.task
def pay_order():
    print('=====开始下单=====')
    time.sleep(5)
    print('=====下单成功=====')
    return '下单成功!'
