from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.models import Users
from app.modules.config.services.auth import get_current_active_user
from app.modules.news.schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from app.modules.news.services.favorite import check_favorite_exists, add_favorite, remove_favorite, get_favorite_list, \
    clear_favorite_list
from app.utils.database import get_db
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/favorite",
    tags=["收藏"],
    dependencies=[Depends(get_current_active_user)],
)


# 检查用户是否收藏了该新闻
@router.get("/check")
async def check_favorite_route(
        news_id: int = Query(..., description="新闻ID"),
        user: Users = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    is_favorite = await check_favorite_exists(db, news_id, user.id)  # is_favorite 是 bool，表示当前用户是否已收藏该新闻
    """
    这里用 FavoriteCheckResponse 模型类封装is_favorite数据
    主要是为了统一响应字段格式，尤其是把后端 Python 的蛇形命名转换成前端常用的驼峰命名。

    如果直接返回 data = is_favorite 不够直观，也不利于拓展返回的数据
    """
    response_data = FavoriteCheckResponse(is_favorite=is_favorite)
    return success_response(
        message="检查收藏状态成功",
        data=response_data
    )


# 定义添加收藏的POST接口
@router.post("/add")
async def add_favorite_route(
        data: FavoriteAddRequest,  # 接收收藏请求数据
        user: Users = Depends(get_current_active_user),  # 注入当前用户
        db: AsyncSession = Depends(get_db),  # 注入数据库会话
):
    # 调用CRUD函数添加收藏
    result = await add_favorite(db, user.id, data.news_id)

    # 返回成功响应
    return success_response(data=result, message="收藏成功")


# 取消收藏
@router.delete("/remove")
async def remove_favorite_route(
        news_id: int = Query(..., description="新闻ID"),  # 接收文章ID查询参数，必填
        user: Users = Depends(get_current_active_user),  # 注入当前用户
        db: AsyncSession = Depends(get_db)  # 注入数据库会话
):
    # 调用CRUD函数取消收藏
    result = await remove_favorite(db, user.id, news_id)

    if not result:
        return HTTPException(status_code=404, detail="无收藏结果")

    return success_response(data=result, message="取消收藏成功")


# 定义获取收藏列表的GET接口
@router.get("/list")
async def get_favorite_list_route(
        page: int = Query(1, ge=1, description="页码"),  # 接收页码参数，默认为1
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),  # 接收每页数量参数，默认为10
        user: Users = Depends(get_current_active_user),  # 注入当前用户
        db: AsyncSession = Depends(get_db)  # 获取数据库会话
):
    # rows 是ORM模型对象列表，需要转换成字典列表返给前端
    rows, total = await get_favorite_list(db, user.id, page, page_size)

    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id
        }
        for news, favorite_time, favorite_id in rows
    ]

    has_more = total > page * page_size

    data = FavoriteListResponse(
        list=favorite_list,
        total=total,
        has_more=has_more
    )
    return success_response(data=data, message="获取收藏列表成功")


# 清空收藏列表
@router.delete("/clear")
async def clear_favorite_route(
        user: Users = Depends(get_current_active_user),  # 注入当前用户
        db: AsyncSession = Depends(get_db)  # 获取数据库会话
):
    count = await clear_favorite_list(db, user.id)
    return success_response(message=f"清空了{count}条记录")
