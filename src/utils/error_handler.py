#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理器模块
提供统一的错误处理和异常管理
"""

import sys
import traceback
import functools
from typing import Any, Callable, Optional, Dict
from enum import Enum


class ErrorSeverity(Enum):
    """错误严重级别"""
    INFO = "INFO"       # 信息
    WARNING = "WARNING" # 警告
    ERROR = "ERROR"     # 错误
    CRITICAL = "CRITICAL" # 严重错误


class ErrorCode(Enum):
    """错误代码枚举"""
    # 通用错误
    UNKNOWN_ERROR = ("E0001", "未知错误")
    CONFIG_ERROR = ("E0002", "配置错误")
    FILE_NOT_FOUND = ("E0003", "文件不存在")
    PERMISSION_ERROR = ("E0004", "权限错误")
    NETWORK_ERROR = ("E0005", "网络错误")
    
    # AI相关错误
    AI_CONNECTION_ERROR = ("E1001", "AI连接失败")
    AI_RESPONSE_ERROR = ("E1002", "AI响应错误")
    AI_MODEL_ERROR = ("E1003", "AI模型错误")
    
    # 内存相关错误
    MEMORY_READ_ERROR = ("E2001", "记忆读取失败")
    MEMORY_WRITE_ERROR = ("E2002", "记忆写入失败")
    MEMORY_CORRUPTED = ("E2003", "记忆数据损坏")
    
    # 心情相关错误
    MOOD_ANALYSIS_ERROR = ("E3001", "心情分析失败")
    MOOD_IMAGE_ERROR = ("E3002", "心情图片错误")
    MOOD_STATE_ERROR = ("E3003", "心情状态错误")
    
    # UI相关错误
    UI_RENDER_ERROR = ("E4001", "UI渲染失败")
    UI_EVENT_ERROR = ("E4002", "UI事件错误")
    UI_CONFIG_ERROR = ("E4003", "UI配置错误")
    
    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description


class AIError(Exception):
    """AI宠物自定义异常基类"""
    
    def __init__(self, 
                 error_code: ErrorCode,
                 message: str = "",
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 original_error: Optional[Exception] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        初始化自定义异常
        
        Args:
            error_code: 错误代码
            message: 错误消息
            severity: 错误严重级别
            original_error: 原始异常
            context: 错误上下文信息
        """
        self.error_code = error_code
        self.message = message or error_code.description
        self.severity = severity
        self.original_error = original_error
        self.context = context or {}
        self.timestamp = None
        self.traceback = None
        
        # 生成完整错误消息
        full_message = f"[{error_code.code}] {self.message}"
        if original_error:
            full_message += f" (原始错误: {str(original_error)})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.error_code.code,
            "message": self.message,
            "severity": self.severity.value,
            "original_error": str(self.original_error) if self.original_error else None,
            "context": self.context,
            "timestamp": self.timestamp,
            "traceback": self.traceback
        }


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger=None):
        """
        初始化错误处理器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self.error_counters = {}
        self.error_history = []
        self.max_history_size = 1000
    
    def handle_error(self, 
                    error: Exception,
                    operation: str = "",
                    context: Optional[Dict] = None,
                    raise_exception: bool = True) -> Optional[AIError]:
        """
        处理错误
        
        Args:
            error: 异常对象
            operation: 操作描述
            context: 上下文信息
            raise_exception: 是否重新抛出异常
        
        Returns:
            AIError对象或None
        """
        # 确定错误代码
        error_code = self._classify_error(error)
        
        # 创建自定义异常
        ai_error = AIError(
            error_code=error_code,
            message=str(error),
            original_error=error,
            context=context or {}
        )
        
        # 记录错误信息
        ai_error.timestamp = self._get_timestamp()
        ai_error.traceback = self._get_traceback(error)
        
        # 更新计数器
        self._increment_counter(error_code)
        
        # 记录到历史
        self._add_to_history(ai_error)
        
        # 记录日志
        self._log_error(ai_error, operation)
        
        # 如果需要，重新抛出
        if raise_exception:
            raise ai_error from error
        
        return ai_error
    
    def _classify_error(self, error: Exception) -> ErrorCode:
        """分类错误类型"""
        error_str = str(error).lower()
        
        # 检查常见错误类型
        if isinstance(error, FileNotFoundError):
            return ErrorCode.FILE_NOT_FOUND
        elif isinstance(error, PermissionError):
            return ErrorCode.PERMISSION_ERROR
        elif "connection" in error_str or "network" in error_str:
            return ErrorCode.NETWORK_ERROR
        elif "config" in error_str:
            return ErrorCode.CONFIG_ERROR
        elif "ai" in error_str or "model" in error_str:
            if "connection" in error_str:
                return ErrorCode.AI_CONNECTION_ERROR
            else:
                return ErrorCode.AI_RESPONSE_ERROR
        elif "memory" in error_str:
            return ErrorCode.MEMORY_READ_ERROR
        elif "mood" in error_str:
            return ErrorCode.MOOD_ANALYSIS_ERROR
        elif "ui" in error_str or "qt" in error_str:
            return ErrorCode.UI_RENDER_ERROR
        
        return ErrorCode.UNKNOWN_ERROR
    
    def _increment_counter(self, error_code: ErrorCode) -> None:
        """增加错误计数器"""
        code = error_code.code
        if code in self.error_counters:
            self.error_counters[code] += 1
        else:
            self.error_counters[code] = 1
    
    def _add_to_history(self, error: AIError) -> None:
        """添加到错误历史"""
        self.error_history.append(error.to_dict())
        
        # 限制历史记录大小
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _log_error(self, error: AIError, operation: str = "") -> None:
        """记录错误日志"""
        if not self.logger:
            return
        
        log_message = f"操作失败: {operation}" if operation else "发生错误"
        log_message += f" [{error.error_code.code}] {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, **error.context)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message, **error.context)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message, **error.context)
        else:
            self.logger.info(log_message, **error.context)
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_traceback(self, error: Exception) -> str:
        """获取堆栈跟踪"""
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        total_errors = sum(self.error_counters.values())
        recent_errors = len(self.error_history)
        
        return {
            "total_errors": total_errors,
            "recent_errors": recent_errors,
            "error_counts": self.error_counters,
            "error_types": list(self.error_counters.keys())
        }
    
    def get_recent_errors(self, limit: int = 10) -> list:
        """获取最近的错误"""
        return self.error_history[-limit:] if self.error_history else []
    
    def clear_history(self) -> None:
        """清空错误历史"""
        self.error_history.clear()
        self.error_counters.clear()
    
    def safe_execute(self, 
                    func: Callable,
                    operation: str = "",
                    default_return: Any = None,
                    raise_exception: bool = False,
                    **kwargs) -> Any:
        """
        安全执行函数
        
        Args:
            func: 要执行的函数
            operation: 操作描述
            default_return: 异常时的默认返回值
            raise_exception: 是否抛出异常
            **kwargs: 函数参数
        
        Returns:
            函数结果或默认值
        """
        try:
            return func(**kwargs)
        except Exception as e:
            if raise_exception:
                self.handle_error(e, operation, kwargs, raise_exception=True)
            else:
                error = self.handle_error(e, operation, kwargs, raise_exception=False)
                if self.logger:
                    self.logger.warning(f"安全执行返回默认值: {default_return}")
                return default_return
    
    def wrap_function(self, 
                     func: Callable,
                     operation: str = "",
                     raise_exception: bool = True) -> Callable:
        """
        包装函数，自动处理错误
        
        Args:
            func: 要包装的函数
            operation: 操作描述
            raise_exception: 是否抛出异常
        
        Returns:
            包装后的函数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if raise_exception:
                    return self.handle_error(e, operation, kwargs, raise_exception=True)
                else:
                    self.handle_error(e, operation, kwargs, raise_exception=False)
                    return None
        
        return wrapper


# 全局错误处理器实例
_error_handler_instance = None


def get_error_handler(logger=None) -> ErrorHandler:
    """获取错误处理器实例（单例模式）"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler(logger)
    elif logger and not _error_handler_instance.logger:
        _error_handler_instance.logger = logger
    
    return _error_handler_instance


def safe_call(func: Callable = None, 
              operation: str = "",
              default_return: Any = None,
              raise_exception: bool = False):
    """
    安全调用装饰器
    
    Args:
        func: 要装饰的函数
        operation: 操作描述
        default_return: 异常时的默认返回值
        raise_exception: 是否抛出异常
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            handler = get_error_handler()
            return handler.safe_execute(
                lambda: f(*args, **kwargs),
                operation=operation or f.__name__,
                default_return=default_return,
                raise_exception=raise_exception
            )
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def setup_global_exception_handler(logger=None):
    """设置全局异常处理器"""
    handler = get_error_handler(logger)
    
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """全局异常处理函数"""
        # 不处理键盘中断
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 处理异常
        error = AIError(
            error_code=ErrorCode.UNKNOWN_ERROR,
            message=str(exc_value),
            original_error=exc_value
        )
        error.traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        handler._add_to_history(error)
        
        if handler.logger:
            handler.logger.critical(f"未捕获的异常: {exc_type.__name__}", 
                                  error=str(exc_value),
                                  traceback=error.traceback)
        
        # 调用默认的异常处理器
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # 设置全局异常处理器
    sys.excepthook = global_exception_handler
    
    return handler