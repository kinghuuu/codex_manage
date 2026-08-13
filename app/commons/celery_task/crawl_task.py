import time
from .celery import app  # .表示当前路径, 当前路径下的celery文件


@app.task
def crawl_baidu():
    print('=====开始爬百度=====')
    time.sleep(2)
    print('=====爬百度成功=====')
    return '爬取百度成功!'


@app.task
def crawl_csdnblog():
    print('=====开始爬csdn=====')
    time.sleep(2)
    print('=====爬csdn成功=====')
    return '爬取csdn成功!'
