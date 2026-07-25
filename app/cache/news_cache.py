"""
新闻相关的缓存方法：新闻分类的读取和写入
"""
from typing import List, Dict, Any, Optional

from app.utils.cache_conf import get_json_cache, set_cache

# key - value
CATEGORIES_KEY = "news:categories"  # 新闻分类的缓存key
NEWS_LIST_PREFIX = "news_list:"  # 新闻列表的缓存前缀
NEWS_DETAIL_PREFIX = "news:detail:"  # 新闻详情的缓存前缀
RELATED_NEWS_PREFIX = "news:related:"  # 相关推荐新闻的缓存前缀


# 获取新闻分类缓存
async def get_categories_cache():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存: 缓存的数据、过期时间(7200表示2小时)
# 常见的： 分类、配置： 7200；  列表： 600；   详情： 1800；   验证码：120 -- 数据越稳定，缓存越持久
# 避免所有key同时过期，引起缓存雪崩
async def set_categories_cache(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 新闻列表 读取缓存
async def get_news_list_cache(
        category_id: Optional[int],
        page: int,
        page_size: int
):
    category_id_value = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_id_value}:{page}:{page_size}"
    return await get_json_cache(key)


# 新闻列表 写入缓存
# key = news_list:分类id:页码:每页数量 、列表数据 、过期时间
async def set_news_list_cache(
        category_id: Optional[int],
        page: int,
        page_size: int,
        data: List[Dict[str, Any]],
        expire: int = 1800
):
    category_id_value = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_id_value}:{page}:{page_size}"
    return await set_cache(key, data, expire)


# 读取缓存-新闻详情
# key = news:detail:新闻id
async def get_news_detail_cache(news_id: int) -> Optional[Dict[str, Any]]:
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)


# 写入缓存-新闻详情
# key = news:detail:新闻id 、 新闻数据 、 过期时间
async def set_news_detail_cache(
        news_id: int,
        data: Dict[str, Any],
        expire: int = 600
) -> bool:
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key, data, expire)


# 读取缓存-相关新闻
# key = news:related:新闻id:分类id
async def get_related_news_cache(
        news_id: int,
        category_id: int
) -> Optional[List[Dict[str, Any]]]:
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await get_json_cache(key)


# 写入缓存-相关新闻
# key = news:related:新闻id:分类id 、 相关新闻数据 、 过期时间
async def set_related_news_cache(
        news_id: int,
        category_id: int,
        data: List[Dict[str, Any]],
        expire: int = 1800
) -> bool:
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await set_cache(key, data, expire)
