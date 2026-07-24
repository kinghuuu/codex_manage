"""
JWT 其实定义了一种基于 Token 的会话方式，也就是通过一种规则说明了
使用这种Token的标准以及 Token 如何生成和解码。
我们就是通过代码来实现这个会话规则。

JWT 是base64编码，不是加密，所以敏感信息不要放在 payload 中
"""
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

SECRET_KEY = 'a9e734e440dac86c4384c87a6bfd6c977e6fa290308a00c894ae9104b81190a9'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token 过期时间30分钟

# tokenUrl 只是个“指路牌”，你把它改成你真实的登录接口路径（如 /api/v1/auth/login）即可，这样你的 Swagger 文档会更专业、更规范
# OAuth2PasswordBearer 表示通过请求头来获取用户Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_user_token(data: dict):
    """
    创建用户Token
    """
    to_encode = data.copy()

    to_encode.update({
        'exp': datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    })

    encode_jwt = jwt.encode(
        to_encode,  # 要通过Token传输的数据，这里不要放敏感信息
        SECRET_KEY,  # JWT签名的密钥
        algorithm=ALGORITHM  # JWT签名的算法
    )
    return encode_jwt


def get_user_token(token: str = Depends(oauth2_scheme)):
    """
    获取用户Token
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
