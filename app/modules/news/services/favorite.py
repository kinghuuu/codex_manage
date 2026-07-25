from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.news.models.favorite import Favorite
from app.modules.news.models.news import News


# 检查收藏状态
async def check_favorite_exists(
        db: AsyncSession,
        news_id: int,
        user_id: int,
):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    # 是否有收藏记录
    # is not None 对返回结果进行布尔判断
    # 如果查到了数据（返回了具体的值），具体值 is not None 的结果为 True
    # 如果没有查到数据（返回了 None），None is not None 的结果为 False
    return result.scalar_one_or_none() is not None


# 定义添加收藏的函数
async def add_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int,
):
    # 创建收藏对象
    favorite = Favorite(
        news_id=news_id,
        user_id=user_id,
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


# 定义取消收藏的函数
async def remove_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int,
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # 返回是否删除成功


# 定义获取收藏列表的函数
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
):
    # 获取收藏列表总量
    count_stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # 获取收藏列表 - 联表查询 join() + 收藏时间排序 + 分页
    # select(查询主体模型类, 字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 别名： Favorite.created_at.label("favorite_time")
    offset = (page - 1) * page_size
    query = (
        select(
            News,
            Favorite.created_at.label("favorite_time"),
            Favorite.id.label("favorite_id"),
        ).join(
            Favorite,
            Favorite.news_id == News.id,
        ).where(
            Favorite.user_id == user_id,
        ).order_by(
            Favorite.created_at.desc(),
        ).offset(
            offset,
        ).limit(
            page_size,
        )
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 清空收藏列表
async def clear_favorite_list(
        db: AsyncSession,
        user_id: int,
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
