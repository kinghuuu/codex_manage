from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Index, Text, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# 定义ORM基类, 所有新闻相关模型都继承自此类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # 指定字段类型为DateTime
        server_default=func.now(),  # 设置数据库层面的默认值为当前时间
        comment="创建时间",  # 添加字段注释说明
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # 指定字段类型为DateTime
        server_default=func.now(),  # 设置数据库层面的默认值为当前时间
        onupdate=func.now(),  # 当记录更新时自动更新为当前时间
        comment="更新时间",  # 添加字段注释说明
    )


# 新闻分类表
class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类ID",
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="分类名称",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序",
    )

    # 一对多关系
    news_list: Mapped[list["News"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )


# 新闻表
class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询速度 → 添加目录
    __table_args__ = (
        Index("idx_news_category_id", "category_id"),
        Index("idx_news_publish_time", "publish_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news_category.id", ondelete="RESTRICT", ),
        nullable=False,
        comment="分类ID"
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), comment="发布时间")

    # 多对一关系
    category: Mapped["NewsCategory"] = relationship(
        back_populates="news_list"
    )
