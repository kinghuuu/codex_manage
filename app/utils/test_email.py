"""
测试邮件发送功能
"""
import os
import smtplib
import ssl as ssl_module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.utils.logger import get_logger
from app.utils.response import success_response, fail_response

load_dotenv()

router = APIRouter(prefix="/email", tags=["邮件测试"])

logger = get_logger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "1") == "1"


class EmailSendRequest(BaseModel):
    to_email: str
    subject: str = "测试邮件"
    body: str = "这是一封测试邮件，来自 Codex Manage。"
    body_type: str = "plain"


def send_email(
    to_email: str,
    subject: str,
    body: str,
    body_type: str = "plain",
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    use_ssl: Optional[bool] = None,
) -> None:
    host = smtp_host or SMTP_HOST
    port = smtp_port or SMTP_PORT
    user = smtp_user or SMTP_USER
    pwd = smtp_password or SMTP_PASSWORD
    use_tls = use_ssl if use_ssl is not None else SMTP_USE_SSL

    if not user or not pwd:
        raise ValueError("SMTP 发件邮箱或密码未配置")

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr(("HJ", user))
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, body_type, "utf-8"))

    logger.info("正在连接 %s:%s ...", host, port)

    if use_tls:
        ctx = ssl_module.create_default_context()
        with smtplib.SMTP_SSL(host, port, timeout=30, context=ctx) as server:
            server.login(user, pwd)
            server.sendmail(user, [to_email], msg.as_string())
    else:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, pwd)
            server.sendmail(user, [to_email], msg.as_string())

    logger.info("邮件发送成功 -> %s", to_email)


@router.post("/send", summary="发送测试邮件")
async def send_email_router(req: EmailSendRequest = Body(...)):
    try:
        send_email(to_email=req.to_email, subject=req.subject, body=req.body, body_type=req.body_type)
        return success_response(message="邮件已发送至 " + req.to_email)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP 认证失败")
        return fail_response(code=502, message="SMTP 认证失败，请检查用户名或授权码")
    except (smtplib.SMTPConnectError, TimeoutError, OSError):
        logger.exception("SMTP 连接失败")
        return fail_response(code=502, message="无法连接 SMTP 服务器，请检查网络或服务器地址")
    except smtplib.SMTPException:
        logger.exception("SMTP 发送失败")
        return fail_response(code=502, message="邮件发送失败")
    except Exception:
        logger.exception("发送邮件时发生未知错误")
        return fail_response(code=500, message="服务器内部错误")


@router.get("/config", summary="查看 SMTP 配置")
async def config_router():
    return success_response(data={
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "user": SMTP_USER if SMTP_USER else "(未配置)",
        "use_ssl": SMTP_USE_SSL,
    })
