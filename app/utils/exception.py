"""
异常处理模块
"""

import traceback  # 导入traceback模块用于格式化异常信息
from fastapi import HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status  # 导入Starlette状态码常量

# True 开发模式：返回详细错误信息
# False 生产模式：返回简化错误信息
DEBUG_MODE = True


# 定义HTTP异常处理器
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,  # 设置HTTP状态码
        content={
            "code": exc.status_code,  # 返回错误码
            "message": exc.detail,  # 返回错误详情
            "data": None  # data字段为None
        }
    )


# 定义数据库完整性约束错误处理器
async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_msg = str(exc.orig)  # 获取原始错误信息

    # 判断具体的约束错误类型并进行语义化转换
    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"  # 用户名重复错误
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"  # 外键约束错误
    else:
        detail = "数据约束冲突,请检查输入"  # 其他约束错误

    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",  # 错误类型
            "error_detail": error_msg,  # 错误详情
            "path": str(request.url)  # 请求路径
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  # 设置400状态码
        content={
            "code": 400,  # 返回错误码
            "message": detail,  # 返回错误消息
            "data": error_data  # 返回详细错误数据
        }
    )


# 定义SQLAlchemy数据库通用错误处理器
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,  # 错误类型名称
            "error_detail": str(exc),  # 错误详情
            "traceback": traceback.format_exc(),  # 异常堆栈跟踪
            "path": str(request.url)  # 请求路径
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # 设置500状态码
        content={
            "code": 500,  # 返回错误码
            "message": "数据库操作失败,请稍后重试",  # 返回错误消息
            "data": error_data  # 返回详细错误数据
        }
    )


# 定义所有未捕获的其它通用异常处理器
async def general_exception_handler(request: Request, exc: Exception):
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,  # 错误类型名称
            "error_detail": str(exc),  # 错误详情
            "traceback": traceback.format_exc(),  # 格式化异常信息为字符串方便日志记录和调试
            "path": str(request.url)  # 请求路径
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # 设置500状态码
        content={
            "code": 500,  # 返回错误码
            "message": "服务器内部错误",  # 返回错误消息
            "data": error_data  # 返回详细错误数据
        }
    )


# 定义注册异常处理器的封装函数
def register_exceptions(app: FastAPI):
    """
    注册全局异常处理：子类在前，父类在后；具体在前，抽象在后
    """
    app.add_exception_handler(HTTPException, http_exception_handler)  # 业务，将HTTP异常处理器注册到FastAPI实例
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # 数据完整性，将完整性错误处理器注册到FastAPI实例
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)  # 数据库，将SQLAlchemy错误处理器注册到FastAPI实例
    app.add_exception_handler(Exception, general_exception_handler)  # 兜底，将通用异常处理器注册到FastAPI实例
