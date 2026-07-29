from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.models.user import Users
from app.modules.config.schemas.user import UserCreate, UserLogin, UserRegister
from app.modules.config.services.user import create_user, get_user_by_username, serialize_user
from app.utils.database import get_db
from app.utils.jwt import create_user_token, get_user_token
from app.utils.logger import get_logger
from app.utils.security import PasswordUtils

logger = get_logger(__name__)


async def login(db: AsyncSession, user_data: UserLogin) -> dict:
    logger.info("login服务: username=%s", user_data.username)

    """用户登录"""
    user = await get_user_by_username(db, user_data.username)

    if user is None or not PasswordUtils.check_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    token = create_user_token({"user_id": user.id, "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


async def register(db: AsyncSession, user_data: UserRegister) -> dict:
    """用户注册"""
    create_data = UserCreate(
        username=user_data.username,
        password=user_data.password,
        phone=user_data.phone,
        email=user_data.email,
        real_name=user_data.real_name,
    )
    return await create_user(db, create_data)


async def get_current_active_user(
        db: AsyncSession = Depends(get_db),
        token_data: dict = Depends(get_user_token),
) -> Users:
    """获取当前用户"""
    user_id = token_data.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(Users, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已删除",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user
