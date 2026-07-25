from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.config.services.auth import get_current_active_user
from app.modules.news.services.news import get_news_categories, get_news_list, get_news_count, get_news_detail, \
    increase_news_views, get_related_news
from app.utils.datebase import get_db
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/news",
    tags=["新闻"],
    dependencies=[Depends(get_current_active_user)],
)


# 获取新闻分类
@router.get("/categories", summary="获取新闻分类")
async def get_news_categories_router(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(100, ge=1, description="每页数量"),
        db: AsyncSession = Depends(get_db)
):
    categories = await get_news_categories(db, page, page_size)
    if not categories:
        raise HTTPException(status_code=404, detail="新闻分类不存在")

    return success_response(
        data=categories,
        message="删除历史记录成功",
    )


# 获取新闻列表, 分页查询
@router.get("/list", summary="获取新闻列表")
async def get_news_list_router(
        category_id: int = Query(..., description="分类ID"),  # ... 表示该参数是必填的
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(100, ge=1, description="每页数量"),
        db: AsyncSession = Depends(get_db)
):
    news_list = await get_news_list(db, category_id, page, page_size)
    if not news_list:
        raise HTTPException(status_code=404, detail="新闻列表为空")

    total = await get_news_count(db, category_id)

    # （跳过的 + 当前列表里面的数量）< 总量
    offset = (page - 1) * page_size
    has_more = (offset + len(news_list)) < total

    return success_response(
        data={
            "list": news_list,
            "hasMore": has_more,
            "total": total
        },
        message="获取新闻列表成功",
    )


# 获取新闻详情
@router.get("/detail", summary="获取新闻详情")
async def get_news_detail_router(
        news_id: int = Query(..., description="新闻ID"),
        db: AsyncSession = Depends(get_db)
):
    news_detail = await get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_result = await increase_news_views(db, news_id)
    if not views_result:
        raise HTTPException(status_code=500, detail="更新新闻浏览量失败")

    related_news = await get_related_news(db, news_id, news_detail.category_id)

    data = {
        "id": news_detail.id,
        "title": news_detail.title,
        "description": news_detail.description,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
    }

    return success_response(
        data=data,
        message="获取新闻详情成功",
    )
