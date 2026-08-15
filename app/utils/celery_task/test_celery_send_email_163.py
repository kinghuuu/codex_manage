import os
import smtplib
import socket
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

# 项目根目录：当前文件位于 app/utils/celery_task/ 下，向上推 3 级
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 发件方 163 邮箱，真实账号建议放在 .env 的 SMTP_163_USER 中
msg_from = os.getenv("SMTP_163_USER", "")
# 163 邮箱授权码，只放在 .env，不写入代码
password = os.getenv("SMTP_163_PASSWORD", "")
# 收件人列表，默认发给 QQ 邮箱用于测试
msg_to_list = ["761751953@qq.com"]


def send_email_with_retry(max_retries=3):
    if not msg_from or not password:
        print("请先在 .env 中配置 SMTP_163_USER 和 SMTP_163_PASSWORD")
        return False

    subject = "邮件标题12"
    content = "邮件内容123456789"

    # 生成一个 MIMEText 对象，'plain' 表示纯文本，也可以用 'html'
    # msg = MIMEText(content, "plain", "utf-8")
    # 创建一个带附件的实例
    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = msg_from
    msg["To"] = ",".join(msg_to_list)

    # 邮件正文内容
    msg.attach(MIMEText(content, "plain", "utf-8"))
    # 添加附件添加项目根目录下的 resource\test.md
    attach_file_path = PROJECT_ROOT / "resource" / "test.md"
    with open(attach_file_path, "r", encoding="utf-8") as f:
        attach_file = MIMEText(f.read(), "base64", "utf-8")
        attach_file["Content-Type"] = "application/octet-stream"
        attach_file["Content-Disposition"] = f"attachment; filename={attach_file_path.name}"
        msg.attach(attach_file)

    # 添加图片附件，添加项目根目录下的 resource\1.jpeg
    # JPEG 是二进制文件，改用 MIMEBase + Base64 编码发送
    attach_file_path = PROJECT_ROOT / "resource" / "1.jpeg"
    with open(attach_file_path, "rb") as f:
        attach_file = MIMEBase("application", "octet-stream")
        attach_file.set_payload(f.read())
        encoders.encode_base64(attach_file)
        attach_file["Content-Disposition"] = f"attachment; filename={attach_file_path.name}"
        msg.attach(attach_file)

    # 163 邮箱默认使用 465 SSL，也可以通过环境变量覆盖
    smtp_configs = [
        {
            "host": os.getenv("SMTP_163_HOST", "smtp.163.com"),
            "port": int(os.getenv("SMTP_163_PORT", "465")),
            "use_ssl": os.getenv("SMTP_163_USE_SSL", "1") == "1",
        },
    ]

    for config in smtp_configs:
        for attempt in range(max_retries):
            try:
                print(f"尝试连接 {config['host']}:{config['port']} (尝试 {attempt + 1}/{max_retries})")

                if config["use_ssl"]:
                    s = smtplib.SMTP_SSL(config["host"], config["port"], timeout=30)
                else:
                    s = smtplib.SMTP(config["host"], config["port"], timeout=30)
                    s.ehlo()
                    s.starttls()
                    s.ehlo()

                with s:
                    print(f"实际使用账号: '{msg_from}'")
                    s.login(msg_from, password)
                    s.sendmail(msg_from, msg_to_list, msg.as_string())
                    print(f"发送成功 (使用端口 {config['port']})")
                    return True

            except socket.timeout:
                print(f"连接超时 (端口 {config['port']})")
            except smtplib.SMTPAuthenticationError as e:
                print(f"认证失败，请检查 163 邮箱授权码: {e}")
                return False
            except smtplib.SMTPException as e:
                print(f"SMTP错误 (端口 {config['port']}): {e}")
            except Exception as e:
                print(f"错误 (端口 {config['port']}): {e}")

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待{wait_time}秒后重试...")
                time.sleep(wait_time)

        print(f"端口 {config['port']} 尝试失败")

    print("所有端口和重试均失败")
    return False


if __name__ == '__main__':
    send_email_with_retry()
