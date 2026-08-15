import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import time
import socket

load_dotenv()  # 加载环境变量

# 发件方邮箱
msg_from = "761751953@qq.com"
# 授权码
password = os.getenv("SMTP_PASSWORD", "")
# 支持发送给多个人
msg_to_list = ["18951825120@163.com"]


def send_email_with_retry(max_retries=3):
    subject = "测试邮件1"
    content = "邮件内容1"

    # 生成一个MIMEText对象
    # 'plain' 表示纯文本，也可以用 'html'
    msg = MIMEText(content, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = msg_from
    msg['To'] = ",".join(msg_to_list)

    # 尝试两种端口方案
    smtp_configs = [
        {"host": "smtp.qq.com", "port": 465, "use_ssl": True},
        {"host": "smtp.qq.com", "port": 587, "use_ssl": False},
    ]

    for config in smtp_configs:
        for attempt in range(max_retries):
            try:
                print(f"📡 尝试连接 {config['host']}:{config['port']} (尝试 {attempt + 1}/{max_retries})")

                if config["use_ssl"]:
                    s = smtplib.SMTP_SSL(config["host"], config["port"], timeout=30)
                else:
                    s = smtplib.SMTP(config["host"], config["port"], timeout=30)
                    s.ehlo()
                    s.starttls()
                    s.ehlo()

                with s:
                    print(f"实际使用的密码: '{password}'")
                    s.login(msg_from, password)
                    s.sendmail(msg_from, msg_to_list, msg.as_string())
                    print(f"✅ 发送成功 (使用端口 {config['port']})")
                    return True

            except socket.timeout:
                print(f"⏰ 连接超时 (端口 {config['port']})")
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ 认证失败，请检查授权码: {e}")
                return False
            except smtplib.SMTPException as e:
                print(f"❌ SMTP错误 (端口 {config['port']}): {e}")
            except Exception as e:
                print(f"❌ 错误 (端口 {config['port']}): {e}")

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⏳ 等待{wait_time}秒后重试...")
                time.sleep(wait_time)

        print(f"端口 {config['port']} 尝试失败，切换到下一个端口...\n")

    print("❌ 所有端口和重试均失败")
    return False


if __name__ == '__main__':
    send_email_with_retry()
