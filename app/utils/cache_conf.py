
import json
import os
from datetime import datetime, date
from typing import Any

import redis.asyncio as redis

from dotenv import load_dotenv

load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))

# 创建 redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # Redis 服务器的主机地址
    port=REDIS_PORT,  # Redis 端口号
    db=REDIS_DB,  # Redis 数据库编号，0~15
    decode_responses=True,  # 是否将字节数据解码为字符串
    # password=None,  # Redis 的密码，如果没有密码，可以设置为 None，也可以注释掉
)


# 读取：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None


# 读取：列表或字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 序列化
        return None
    except Exception as e:
        print(f"获取JSON缓存失败: {e}")
        return None


# 设置缓存 setex(key, expire, value)   下面的3600是秒,默认了1小时
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            # 如果 value 是字典或列表，转字符串再存
            # 这里的json.dumps()是Python内置的json模块，用于将Python对象转换成JSON字符串。
            # 一开始引入的是Pydantic.json，但是Pydantic.json.dumps()不能处理Python对象，只能处理字符串。
            value = json.dumps(value, ensure_ascii=False, default=json_serializer)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return None


# 给 json.dumps() 传入一个 default 参数，提供一个自定义的转换函数
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # 将日期时间对象转换为 ISO 格式字符串


