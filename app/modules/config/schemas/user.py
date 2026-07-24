from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    phone: str | None = Field(default=None, description="手机号")
    email: str | None = Field(default=None, description="邮箱")
    real_name: str | None = Field(default=None, description="姓名")


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    phone: str | None = Field(default=None, description="手机号")
    email: str | None = Field(default=None, description="邮箱")
    real_name: str | None = Field(default=None, description="姓名")
    avatar: str | None = Field(default=None, description="头像")
    gender: str | None = Field(default=None, description="性别")
    remark: str | None = Field(default=None, description="备注")


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, description="用户名")
    password: str | None = Field(default=None, min_length=1, description="密码")
    phone: str | None = Field(default=None, description="手机号")
    email: str | None = Field(default=None, description="邮箱")
    real_name: str | None = Field(default=None, description="姓名")
    avatar: str | None = Field(default=None, description="头像")
    gender: str | None = Field(default=None, description="性别")
    remark: str | None = Field(default=None, description="备注")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    phone: str | None = None
    email: str | None = None
    real_name: str | None = None
    avatar: str | None = None
    gender: str | None = None
    is_superuser: bool
    is_active: bool
    remark: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AuthTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
