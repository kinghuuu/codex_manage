from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.schemas.user import UserLogin, UserRegister
from app.modules.config.services.auth import login, register
from app.utils.database import get_db
from app.utils.logger import get_logger
from app.utils.response import success_response

router = APIRouter(prefix="/api/auth", tags=["认证"])

logger = get_logger(__name__)

@router.post("/login", summary="用户登录")
async def login_router(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    logger.info("login路由: user_data=%s", user_data)
    data = await login(db, user_data)
    return success_response(message="登录成功", data=data)


@router.post("/register", summary="用户注册")
async def register_router(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    data = await register(db, user_data)
    return success_response(message="注册成功", data=data)
