"""
封装返回结果
"""
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


# 成功响应
def success_response(message: str = "success", data: Any = None):
    content = {
        "code": 200,
        "message": message,
        "data": data,
    }
    # JSONResponse把任何FastAPI、Pydantic、ORM对象转换成JSON数据响应: code、 message、 data
    return JSONResponse(
        content=jsonable_encoder(content),
    )


# 失败响应
def fail_response(code: int = 500, message: str = "error", data: Any = None):
    content = {
        "code": code,  # 错误状态码
        "message": message,  # 错误信息
        "data": data,  # 错误数据（如果有）
    }
    return JSONResponse(
        content=jsonable_encoder(content),
    )





