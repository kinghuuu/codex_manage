import time
from .celery import app  # .表示当前路径, 当前路径下的celery文件


@app.task
def send_email(to='761751953@qq.com'):
    print('=====发送邮件=====')
    time.sleep(3)
    print('=====邮件发送成功=====')
    return f'向{to}发送邮件成功'
