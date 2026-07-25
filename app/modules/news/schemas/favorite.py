from datetime import datetime

from pydantic import ConfigDict, BaseModel, Field

from app.modules.news.schemas.news import NewsItemBase


# 定义用户收藏状态响应模型
class FavoriteCheckResponse(BaseModel):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        populate_by_name=True,  # 允许通过别名填充字段
        from_attributes=True  # 支持从ORM对象（如SQLAlchemy）转换数据
    )
    is_favorite: bool = Field(..., alias="isFavorite")  # 定义是否收藏字段，必填


# 定义用户收藏创建请求模型
class FavoriteAddRequest(BaseModel):
    # 定义文章ID字段，必填   （alias="newsId"  这个填了之后，前端请求参数中 news_id 就可以换成 newsId）
    news_id: int = Field(..., description="文章ID")


# 定义收藏新闻项响应模型，继承自新闻基础信息模型
class FavoriteNewsItemResponse(NewsItemBase):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        # 允许通过别名填充字段
        populate_by_name=True,
        # 支持从ORM对象转换数据
        from_attributes=True
    )

    # 定义收藏ID字段，使用别名favoriteId
    favorite_id: int = Field(alias="favoriteId")
    # 定义收藏时间字段，使用别名favoriteTime
    favorite_time: datetime = Field(alias="favoriteTime")


# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    # 配置Pydantic模型行为
    model_config = ConfigDict(
        populate_by_name=True,  # 允许通过别名填充字段
        from_attributes=True  # 支持从ORM对象（如SQLAlchemy）转换数据
    )

    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")
