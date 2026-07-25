from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# 定义新闻基础信息模型
class NewsItemBase(BaseModel):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        # 支持从ORM对象转换数据
        from_attributes=True,
        # 允许通过别名填充字段
        populate_by_name=True
    )

    # 定义新闻ID字段
    id: int
    # 定义新闻标题字段
    title: str
    # 定义新闻描述字段
    description: Optional[str] = None
    # 定义新闻图片URL字段
    image: Optional[str] = None
    # 定义新闻作者字段
    author: Optional[str] = None
    # 定义分类ID字段，使用别名categoryId
    category_id: int = Field(alias="categoryId")
    # 定义浏览量字段
    views: int
    # 定义发布时间字段，使用别名publishedTime
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")
