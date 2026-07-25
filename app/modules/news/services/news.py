from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.news_cache import get_categories_cache, set_categories_cache, get_news_list_cache, set_news_list_cache, \
    get_news_detail_cache, set_news_detail_cache, get_related_news_cache, set_related_news_cache
from app.modules.news.models.news import NewsCategory, News
from app.modules.news.schemas.news import NewsItemBase


# 获取新闻分类
async def get_news_categories(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 100,
):
    # 先尝试从缓存中获取数据
    categories_cache = await get_categories_cache()
    if categories_cache:
        return categories_cache

    skip = (page - 1) * page_size
    stmt = select(NewsCategory).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # scalars()：取出 Category ORM 对象, all()：把查询结果转换成列表返回

    # 写入缓存
    if categories:
        json_categories = jsonable_encoder(categories)
        await set_categories_cache(json_categories)

    return categories


# 获取新闻列表
async def get_news_list(
        db: AsyncSession,
        category_id: int,
        page: int = 1,
        page_size: int = 100,
):
    # 先尝试从缓存中获取数据
    news_list_cache = await get_news_list_cache(category_id, page, page_size)
    if news_list_cache:
        # 这里返回的是ORM
        return [News(**item) for item in news_list_cache]

    skip = (page - 1) * page_size
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list:
        # 方法1： ORM 数据 转换 字典才能写入缓存
        # 方法2： ORM 转成 Pydantic，再转为 字典
        # by_alias=False 不适用别名，保存 Python 风格，因为 Redis 数据是给后端用的
        # Python中命名风格是小写字母加下划线即snake_case，蛇形命名法
        news_data = [
            NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
            for item in news_list
        ]
        await set_news_list_cache(category_id, page, page_size, news_data)

    return news_list


# 获取新闻总数
async def get_news_count(
        db: AsyncSession,
        category_id: int,
):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # scalar_one() 只能有一个值，否则会报错


# 获取新闻详情
async def get_news_detail(
        db: AsyncSession,
        news_id: int,
):
    # 先尝试从缓存获取新闻详情
    news_detail_cache = await get_news_detail_cache(news_id)
    if news_detail_cache:
        return News(**news_detail_cache)  # 将数据转换成ORM

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()  # scalar_one_or_none() 可以有一个或者没有值

    # 写入缓存
    if news:
        news_json = jsonable_encoder(news)
        await set_news_detail_cache(news_id, news_json)

    return news


# 更新新闻浏览量
async def increase_news_views(
        db: AsyncSession,
        news_id: int,
):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新 → 检查数据库是否真的命中了数据 → 命中了返回True
    return result.rowcount > 0


# 获取相关新闻
async def get_related_news(
        db: AsyncSession,
        news_id: int,
        category_id: int,
        limit: int = 5
):
    # 先尝试从缓存中获取数据
    related_news_cache = await get_related_news_cache(news_id, category_id)
    if related_news_cache:
        return related_news_cache

    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),  # 默认是升序，降序是desc()
        News.publish_time.desc()
    ).limit(limit)  # 按浏览量降序，然后按发布时间降序，获取前5条数据

    result = await db.execute(stmt)
    related_news = result.scalars().all()

    related_data = [
        {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "image": item.image,
            "author": item.author,
            "publishTime": item.publish_time,
            "categoryId": item.category_id,
            "views": item.views
        } for item in related_news
    ]

    # 写入缓存
    if related_data:
        await set_related_news_cache(news_id, category_id, related_data)

    return related_data
