"""
API 中间件

提供请求处理、错误处理、认证等中间件功能
"""

import time
import logging
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)


async def setup_middleware(app):
    """设置所有中间件"""
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
            
            # 添加处理时间头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    # 全局异常处理中间件
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "error_message": "Internal server error",
                "details": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # 请求验证错误处理
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc}")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "error_message": "Request validation failed",
                "details": exc.errors(),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # HTTP 异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": "HTTP_ERROR",
                "error_message": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )


def rate_limit(max_requests: int = 100, time_window: int = 60):
    """
    速率限制装饰器
    
    Args:
        max_requests: 最大请求数
        time_window: 时间窗口（秒）
    """
    def decorator(func):
        # 这里可以实现速率限制逻辑
        # 为了简化，暂时返回原函数
        return func
    return decorator


def require_api_key(api_key: str):
    """
    API 密钥验证装饰器
    
    Args:
        api_key: 有效的 API 密钥
    """
    def decorator(func):
        # 这里可以实现 API 密钥验证逻辑
        # 为了简化，暂时返回原函数
        return func
    return decorator