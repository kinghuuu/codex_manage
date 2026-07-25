from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.news.models.history import History
from app.modules.news.models.news import News


# 定义添加浏览记录的函数
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int,
):
    # 创建浏览记录对象
    history = History(
        user_id=user_id,
        news_id=news_id,
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


# 定义获取历史记录列表
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
):
    count_query = select(func.count(History.id)).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size  # 计算偏移量
    query = (
        select(
            News,
            History.view_time.label("history_time"),
            History.id.label("history_id"),
            History.user_id
        ).join(
            History,
            History.news_id == News.id,
        ).where(
            History.user_id == user_id,
        ).order_by(
            History.view_time.desc(),
        ).offset(
            offset,
        ).limit(
            page_size,
        )
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 定义删除单条历史记录的函数
async def delete_history(
        db: AsyncSession,
        user_id: int,
        history_id: int,
):
    stmt = delete(History).where(History.id == history_id, History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 定义清空历史记录的函数
async def clear_history(
        db: AsyncSession,
        user_id: int,
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
