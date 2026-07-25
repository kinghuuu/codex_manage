from datetime import datetime

from sqlalchemy import Index, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.modules.config.models import Users
from app.modules.news.models.news import News


# 定义ORM基类, 所有浏览历史相关模型都继承自此类
class Base(DeclarativeBase):
    pass


# 浏览历史表
class History(Base):
    __tablename__ = "history"

    # 创建索引
    __table_args__ = (
        # 用户历史查询
        Index(
            "idx_history_user_view_time",
            "user_id",
            "view_time",
        ),
        # 新闻浏览记录查询
        Index(
            "idx_history_news_view_time",
            "news_id",
            "view_time",
        ),
    )

    # 定义历史ID字段，作为主键并自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史ID")
    # 定义用户ID字段，作为外键关联到User表
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="用户ID"
    )
    # 定义新闻ID字段，作为外键关联到News表
    news_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="新闻ID"
    )
    # 定义浏览时间字段，默认为当前时间
    view_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="浏览时间"
    )

    # 关系映射
    user: Mapped["Users"] = relationship(
        "Users",
        lazy="select",
    )
    news: Mapped["News"] = relationship(
        "News",
        lazy="select",
    )
