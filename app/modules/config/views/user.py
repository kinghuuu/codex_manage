from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.schemas.user import UserCreate, UserListQuery, UserUpdate
from app.modules.config.services.auth import get_current_active_user
from app.modules.config.services.user import (
    create_user,
    delete_user,
    get_user_by_id,
    list_users,
    serialize_user,
    update_user,
)
from app.utils.datebase import get_db
from app.utils.logger import get_logger
from app.utils.response import success_response

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/users",
    tags=["用户管理"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("", summary="用户列表")
async def list_users_router(
        query: UserListQuery = Depends(),
        db: AsyncSession = Depends(get_db),
):
    logger.info("list users: query=%s", query.model_dump())
    data = await list_users(db, query=query)
    return success_response(message="获取成功", data=data)


@router.get("/{user_id}", summary="用户详情")
async def get_user_router(
        user_id: int,
        db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return success_response(message="获取成功", data=serialize_user(user))


@router.post("", summary="创建用户")
async def create_user_router(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db),
):
    data = await create_user(db, user_data)
    return success_response(message="创建成功", data=data)


@router.put("/{user_id}", summary="更新用户")
async def update_user_router(
        user_id: int,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_db),
):
    data = await update_user(db, user_id, user_data)
    return success_response(message="更新成功", data=data)


@router.delete("/{user_id}", summary="删除用户")
async def delete_user_router(
        user_id: int,
        db: AsyncSession = Depends(get_db),
):
    data = await delete_user(db, user_id)
    return success_response(message="删除成功", data=data)
