from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from app.modules.news.schemas.news import NewsItemBase


# 定义添加浏览记录请求模型
class HistoryAddRequest(BaseModel):
    newsId: int = Field(..., description="新闻ID")  # 定义文章ID字段，必填


# 定义浏览记录项响应模型，继承自新闻基础信息模型
class HistoryNewsItemResponse(NewsItemBase):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        # 允许通过别名填充字段
        populate_by_name=True,
        # 支持从ORM对象转换数据
        from_attributes=True
    )

    history_id: int = Field(alias="historyId")  # 定义历史记录ID字段，使用别名historyId
    history_time: datetime = Field(alias="historyTime")  # 定义浏览时间字段，使用别名viewTime
    user_id: int = Field(alias="userId")


# 定义浏览记录列表响应模型
class HistoryListResponse(BaseModel):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        populate_by_name=True,  # 允许通过别名填充字段
        from_attributes=True  # 支持从ORM对象（如SQLAlchemy）转换数据
    )

    # 定义浏览记录列表字段，默认为空列表
    list: List[HistoryNewsItemResponse] = Field(default_factory=list, description="浏览记录列表")
    # 定义浏览记录总数字段，默认为0
    total: int = Field(default=0, description="浏览记录总数")
    # 定义是否有更多字段，默认为False
    hasMore: bool = Field(default=False, description="是否有更多")
