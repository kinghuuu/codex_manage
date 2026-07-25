from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.models import Users
from app.modules.config.services.auth import get_current_active_user
from app.modules.news.schemas.history import HistoryAddRequest, HistoryNewsItemResponse, HistoryListResponse
from app.modules.news.services.history import add_history, get_history_list, delete_history, clear_history
from app.utils.datebase import get_db
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/history",
    tags=["浏览记录"],
    dependencies=[Depends(get_current_active_user)],
)


# 定义添加浏览记录的POST接口
@router.post("/add")
async def add_history_route(
        data: HistoryAddRequest,
        user: Users = Depends(get_current_active_user),  # 获取当前用户
        db: AsyncSession = Depends(get_db)  # 获取数据库会话
):
    # 调用CRUD函数添加浏览记录
    result = await add_history(db, user.id, data.newsId)

    return success_response(data=result, message="添加浏览记录成功")


# 定义获取历史记录列表的GET接口
@router.get("/list")
async def get_history_list_route(
        page: int = Query(1, ge=1, description="页码"),  # 获取页码参数，默认为1
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),  # 获取每页数量参数，默认为10
        user: Users = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await get_history_list(db, user.id, page, page_size)

    # 判断是否有更多数据
    has_more = total > page * page_size

    # 将查询结果转换为响应模型（处理空数据情况）
    history_list = [
        HistoryNewsItemResponse.model_validate({
            **news.__dict__,
            "history_time": history_time,
            "history_id": history_id,
            "user_id": user_id
        }) for news, history_time, history_id, user_id in rows
    ] if rows else []

    # 构造响应数据
    data = HistoryListResponse(
        list=history_list,
        total=total,
        has_more=has_more
    )

    return success_response(data=data, message="获取历史记录列表成功")


# 定义删除单条历史记录的DELETE接口
@router.delete("/delete")
async def delete_history_route(
        history_id: int = Query(..., description="历史记录ID"),  # 获取历史记录ID参数
        user: Users = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)  # 获取数据库会话
):
    result = await delete_history(db, user.id, history_id)
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    return success_response(
        data=result,
        message="删除历史记录成功",
    )


# 定义清空历史记录的DELETE接口
@router.delete("/clear")
async def clear_history_route(
        user: Users = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)  # 获取数据库会话
):
    count = await clear_history(db, user.id)
    return success_response(message=f"成功清空了{count}条记录")
