from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.modules.config.models import Users
from app.modules.news.models.news import News


# 定义ORM基类, 所有收藏相关模型都继承自此类
class Base(DeclarativeBase):
    pass


class Favorite(Base):
    __tablename__ = "favorite"

    # 定义表的额外参数，如唯一约束和索引
    __table_args__ = (
        # 同一用户不能重复收藏同一新闻
        UniqueConstraint(
            "user_id",
            "news_id",
            name="uk_user_news_favorite",
        ),

        # 查询用户收藏列表
        Index(
            "idx_favorite_user_created",
            "user_id",
            "created_at",
        ),

        # 查询某新闻被收藏情况
        Index(
            "idx_favorite_news",
            "news_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="收藏ID")  # 定义收藏ID字段，作为主键并自动递增
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="分类名称")
    news_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="排序")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
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
