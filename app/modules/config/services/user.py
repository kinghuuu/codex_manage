from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.models.user import Users
from app.modules.config.schemas.user import UserCreate, UserListQuery, UserUpdate
from app.utils.security import PasswordUtils

USER_OUTPUT_FIELDS = (
    "id",
    "username",
    "phone",
    "email",
    "real_name",
    "avatar",
    "gender",
    "is_superuser",
    "is_active",
    "remark",
    "created_at",
    "updated_at",
)


def serialize_user(user: Users) -> dict:
    return {field: getattr(user, field) for field in USER_OUTPUT_FIELDS}


async def get_user_by_id(db: AsyncSession, user_id: int) -> Users | None:
    stmt = select(Users).where(Users.id == user_id).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Users | None:
    stmt = select(Users).where(Users.username == username).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession,
    query: UserListQuery,
) -> dict:
    page = max(query.page, 1)
    page_size = min(max(query.page_size, 1), 100)

    filters = []
    like_fields = (
        (Users.username, query.username),
        (Users.phone, query.phone),
        (Users.real_name, query.real_name),
    )
    for column, value in like_fields:
        if value:
            value = value.strip()
            if value:
                filters.append(column.like(f"%{value}%"))

    total_stmt = select(func.count()).select_from(Users)
    stmt = select(Users)
    if filters:
        total_stmt = total_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = await db.scalar(total_stmt)
    stmt = (
        stmt
        .order_by(Users.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    users = [serialize_user(user) for user in result.scalars().all()]

    return {
        "items": users,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


async def create_user(db: AsyncSession, user_data: UserCreate) -> dict:
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    new_user = Users(
        username=user_data.username,
        password=PasswordUtils.hash_password(user_data.password),
        phone=user_data.phone,
        email=user_data.email,
        real_name=user_data.real_name,
        avatar=user_data.avatar,
        gender=user_data.gender,
        is_superuser=False,
        is_active=True,
        remark=user_data.remark,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return serialize_user(new_user)


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> dict:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    update_data = user_data.model_dump(exclude_unset=True)
    update_data.pop("is_superuser", None)
    update_data.pop("is_active", None)

    if not update_data:
        return serialize_user(user)

    if "username" in update_data and update_data["username"] != user.username:
        existing_user = await get_user_by_username(db, update_data["username"])
        if existing_user is not None and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )

    if "password" in update_data:
        update_data["password"] = PasswordUtils.hash_password(update_data["password"])

    for field_name, field_value in update_data.items():
        setattr(user, field_name, field_value)

    await db.commit()
    await db.refresh(user)
    return serialize_user(user)


async def delete_user(db: AsyncSession, user_id: int) -> dict:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    await db.delete(user)
    await db.commit()
    return {"deleted": True, "user_id": user_id}
