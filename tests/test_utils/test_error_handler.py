#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理器测试
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

from src.utils.error_handler import (
    ErrorHandler, AIError, ErrorCode, ErrorSeverity,
    get_error_handler, safe_call, setup_global_exception_handler
)


class TestAIError:
    """AI错误测试"""
    
    def test_initialization(self):
        """测试初始化"""
        error = AIError(
            error_code=ErrorCode.FILE_NOT_FOUND,
            message="文件不存在",
            severity=ErrorSeverity.ERROR
        )
        
        assert error.error_code == ErrorCode.FILE_NOT_FOUND
        assert error.message == "文件不存在"
        assert error.severity == ErrorSeverity.ERROR
        assert error.original_error is None
        assert error.context == {}
        
        # 检查字符串表示
        assert "[E0003]" in str(error)
        assert "文件不存在" in str(error)
    
    def test_with_original_error(self):
        """测试带原始错误"""
        original = FileNotFoundError("找不到文件")
        
        error = AIError(
            error_code=ErrorCode.FILE_NOT_FOUND,
            original_error=original
        )
        
        assert error.original_error == original
        assert "原始错误" in str(error)
    
    def test_with_context(self):
        """测试带上下文"""
        context = {"filename": "test.txt", "operation": "read"}
        
        error = AIError(
            error_code=ErrorCode.FILE_NOT_FOUND,
            context=context
        )
        
        assert error.context == context
    
    def test_to_dict(self):
        """测试转换为字典"""
        original = ValueError("测试值错误")
        
        error = AIError(
            error_code=ErrorCode.AI_CONNECTION_ERROR,
            message="连接失败",
            severity=ErrorSeverity.CRITICAL,
            original_error=original,
            context={"ip": "localhost", "port": 8080}
        )
        
        error.timestamp = "2024-01-01T00:00:00"
        error.traceback = "模拟堆栈"
        
        error_dict = error.to_dict()
        
        assert error_dict["code"] == "E1001"
        assert error_dict["message"] == "连接失败"
        assert error_dict["severity"] == "CRITICAL"
        assert "测试值错误" in error_dict["original_error"]
        assert error_dict["context"] == {"ip": "localhost", "port": 8080}
        assert error_dict["timestamp"] == "2024-01-01T00:00:00"
        assert error_dict["traceback"] == "模拟堆栈"
    
    def test_error_codes(self):
        """测试所有错误代码"""
        # 检查一些关键错误代码
        assert ErrorCode.FILE_NOT_FOUND.code == "E0003"
        assert ErrorCode.FILE_NOT_FOUND.description == "文件不存在"
        
        assert ErrorCode.AI_CONNECTION_ERROR.code == "E1001"
        assert ErrorCode.AI_CONNECTION_ERROR.description == "AI连接失败"
        
        assert ErrorCode.MOOD_ANALYSIS_ERROR.code == "E3001"
        assert ErrorCode.MOOD_ANALYSIS_ERROR.description == "心情分析失败"
    
    def test_error_severity(self):
        """测试错误严重级别"""
        assert ErrorSeverity.INFO.value == "INFO"
        assert ErrorSeverity.WARNING.value == "WARNING"
        assert ErrorSeverity.ERROR.value == "ERROR"
        assert ErrorSeverity.CRITICAL.value == "CRITICAL"


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        handler = ErrorHandler()
        
        assert handler.logger is None
        assert handler.error_counters == {}
        assert handler.error_history == []
        assert handler.max_history_size == 1000
    
    def test_initialization_with_logger(self):
        """测试带日志器的初始化"""
        mock_logger = Mock()
        handler = ErrorHandler(mock_logger)
        
        assert handler.logger == mock_logger
    
    def test_handle_error_file_not_found(self):
        """测试处理文件不存在错误"""
        handler = ErrorHandler()
        
        error = FileNotFoundError("找不到文件")
        
        with pytest.raises(AIError) as exc_info:
            handler.handle_error(error, operation="读取文件")
        
        ai_error = exc_info.value
        assert ai_error.error_code == ErrorCode.FILE_NOT_FOUND
        assert "找不到文件" in ai_error.message
    
    def test_handle_error_network_error(self):
        """测试处理网络错误"""
        handler = ErrorHandler()
        
        error = ConnectionError("连接失败")
        
        with pytest.raises(AIError) as exc_info:
            handler.handle_error(error, operation="网络请求")
        
        ai_error = exc_info.value
        assert ai_error.error_code == ErrorCode.NETWORK_ERROR
    
    def test_handle_error_ai_connection(self):
        """测试处理AI连接错误"""
        handler = ErrorHandler()
        
        error = ConnectionError("AI连接失败")
        
        with pytest.raises(AIError) as exc_info:
            handler.handle_error(error, operation="连接AI")
        
        ai_error = exc_info.value
        assert ai_error.error_code == ErrorCode.AI_CONNECTION_ERROR
    
    def test_handle_error_with_context(self):
        """测试带上下文的错误处理"""
        handler = ErrorHandler()
        
        error = ValueError("无效值")
        context = {"value": "invalid", "expected": "number"}
        
        with pytest.raises(AIError) as exc_info:
            handler.handle_error(error, operation="验证输入", context=context)
        
        ai_error = exc_info.value
        assert ai_error.context == context
    
    def test_handle_error_no_raise(self):
        """测试不抛出异常的错误处理"""
        mock_logger = Mock()
        handler = ErrorHandler(mock_logger)
        
        error = RuntimeError("运行时错误")
        
        ai_error = handler.handle_error(
            error, 
            operation="测试操作", 
            raise_exception=False
        )
        
        assert isinstance(ai_error, AIError)
        assert ai_error.error_code == ErrorCode.UNKNOWN_ERROR
        
        # 应该记录了日志
        mock_logger.error.assert_called_once()
    
    def test_classify_error(self):
        """测试错误分类"""
        handler = ErrorHandler()
        
        test_cases = [
            (FileNotFoundError("文件"), ErrorCode.FILE_NOT_FOUND),
            (PermissionError("权限"), ErrorCode.PERMISSION_ERROR),
            (ConnectionError("网络"), ErrorCode.NETWORK_ERROR),
            (ValueError("配置"), ErrorCode.CONFIG_ERROR),
            (ConnectionError("AI连接"), ErrorCode.AI_CONNECTION_ERROR),
            (ValueError("AI模型"), ErrorCode.AI_RESPONSE_ERROR),
            (ValueError("内存读取"), ErrorCode.MEMORY_READ_ERROR),
            (ValueError("心情分析"), ErrorCode.MOOD_ANALYSIS_ERROR),
            (RuntimeError("UI渲染"), ErrorCode.UI_RENDER_ERROR),
            (Exception("其他"), ErrorCode.UNKNOWN_ERROR)
        ]
        
        for error, expected_code in test_cases:
            code = handler._classify_error(error)
            assert code == expected_code
    
    def test_error_counting(self):
        """测试错误计数"""
        handler = ErrorHandler()
        
        # 处理几个错误
        for _ in range(3):
            try:
                handler.handle_error(
                    ValueError("测试错误"),
                    raise_exception=False
                )
            except AIError:
                pass
        
        stats = handler.get_error_stats()
        
        assert stats["total_errors"] == 3
        assert "E0001" in stats["error_counts"]  # UNKNOWN_ERROR
        assert stats["error_counts"]["E0001"] == 3
    
    def test_error_history(self):
        """测试错误历史"""
        handler = ErrorHandler()
        
        # 添加一些错误
        for i in range(5):
            try:
                handler.handle_error(
                    ValueError(f"错误{i}"),
                    raise_exception=False
                )
            except AIError:
                pass
        
        recent = handler.get_recent_errors(limit=3)
        
        assert len(recent) == 3
        assert len(handler.error_history) == 5
    
    def test_clear_history(self):
        """测试清空历史"""
        handler = ErrorHandler()
        
        # 添加一些错误
        for _ in range(3):
            try:
                handler.handle_error(ValueError("错误"), raise_exception=False)
            except AIError:
                pass
        
        handler.clear_history()
        
        stats = handler.get_error_stats()
        
        assert stats["total_errors"] == 0
        assert len(handler.error_history) == 0
        assert handler.error_counters == {}
    
    def test_safe_execute_success(self):
        """测试安全执行成功"""
        handler = ErrorHandler()
        
        def successful_func():
            return "结果"
        
        result = handler.safe_execute(
            successful_func,
            operation="成功操作",
            default_return="默认"
        )
        
        assert result == "结果"
    
    def test_safe_execute_failure(self):
        """测试安全执行失败"""
        mock_logger = Mock()
        handler = ErrorHandler(mock_logger)
        
        def failing_func():
            raise ValueError("函数失败")
        
        result = handler.safe_execute(
            failing_func,
            operation="失败操作",
            default_return="默认值",
            raise_exception=False
        )
        
        assert result == "默认值"
        mock_logger.warning.assert_called_once()
    
    def test_safe_execute_raise(self):
        """测试安全执行抛出异常"""
        handler = ErrorHandler()
        
        def failing_func():
            raise RuntimeError("必须失败")
        
        with pytest.raises(AIError):
            handler.safe_execute(
                failing_func,
                operation="必须失败的操作",
                raise_exception=True
            )
    
    def test_wrap_function_success(self):
        """测试包装函数成功"""
        handler = ErrorHandler()
        
        def original_func(x, y):
            return x + y
        
        wrapped = handler.wrap_function(
            original_func,
            operation="加法"
        )
        
        result = wrapped(2, 3)
        
        assert result == 5
    
    def test_wrap_function_failure_raise(self):
        """测试包装函数失败（抛出）"""
        handler = ErrorHandler()
        
        def failing_func():
            raise ValueError("失败")
        
        wrapped = handler.wrap_function(
            failing_func,
            operation="失败操作",
            raise_exception=True
        )
        
        with pytest.raises(AIError):
            wrapped()
    
    def test_wrap_function_failure_no_raise(self):
        """测试包装函数失败（不抛出）"""
        handler = ErrorHandler()
        
        def failing_func():
            raise RuntimeError("静默失败")
        
        wrapped = handler.wrap_function(
            failing_func,
            operation="静默操作",
            raise_exception=False
        )
        
        result = wrapped()
        
        assert result is None


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_error_handler_singleton(self):
        """测试获取错误处理器（单例）"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        assert handler1 is handler2
    
    def test_get_error_handler_with_logger(self):
        """测试带日志器获取错误处理器"""
        mock_logger = Mock()
        
        # 第一次获取（设置日志器）
        handler1 = get_error_handler(mock_logger)
        assert handler1.logger == mock_logger
        
        # 第二次获取（应该相同实例）
        handler2 = get_error_handler()
        assert handler2 is handler1
        assert handler2.logger == mock_logger
    
    def test_safe_call_decorator_success(self):
        """测试安全调用装饰器（成功）"""
        call_count = 0
        
        @safe_call(operation="装饰器测试", default_return="默认")
        def test_function():
            nonlocal call_count
            call_count += 1
            return "成功"
        
        result = test_function()
        
        assert result == "成功"
        assert call_count == 1
    
    def test_safe_call_decorator_failure(self):
        """测试安全调用装饰器（失败）"""
        call_count = 0
        
        @safe_call(operation="失败测试", default_return="默认值")
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("装饰器错误")
        
        result = failing_function()
        
        assert result == "默认值"
        assert call_count == 1
    
    def test_safe_call_decorator_raise(self):
        """测试安全调用装饰器（抛出）"""
        @safe_call(operation="抛出测试", raise_exception=True)
        def failing_function():
            raise RuntimeError("必须抛出")
        
        with pytest.raises(AIError):
            failing_function()
    
    def test_safe_call_as_decorator(self):
        """测试安全调用作为装饰器使用"""
        result = []
        
        @safe_call(default_return="装饰默认")
        def decorated_func():
            result.append("调用")
            raise ValueError("错误")
        
        output = decorated_func()
        
        assert output == "装饰默认"
        assert result == ["调用"]
    
    def test_setup_global_exception_handler(self, monkeypatch):
        """测试设置全局异常处理器"""
        mock_logger = Mock()
        
        # 保存原来的异常处理器
        original_hook = sys.excepthook
        
        try:
            # 设置全局处理器
            handler = setup_global_exception_handler(mock_logger)
            
            assert sys.excepthook != original_hook
            assert handler.logger == mock_logger
            
            # 测试键盘中断（应该调用原始处理器）
            with patch('sys.__excepthook__') as mock_original:
                exc_type = KeyboardInterrupt
                exc_value = KeyboardInterrupt("Ctrl+C")
                exc_traceback = None
                
                sys.excepthook(exc_type, exc_value, exc_traceback)
                
                mock_original.assert_called_once_with(
                    exc_type, exc_value, exc_traceback
                )
            
        finally:
            # 恢复原始处理器
            sys.excepthook = original_hook
    
    def test_global_exception_handler_normal_error(self, monkeypatch):
        """测试全局异常处理器处理普通错误"""
        mock_logger = Mock()
        original_hook = sys.excepthook
        
        try:
            handler = setup_global_exception_handler(mock_logger)
            
            # 模拟异常
            with patch('sys.__excepthook__') as mock_original:
                exc_type = ValueError
                exc_value = ValueError("测试值错误")
                exc_traceback = Mock()
                
                sys.excepthook(exc_type, exc_value, exc_traceback)
                
                # 应该记录了日志
                mock_logger.critical.assert_called_once()
                
                # 应该调用了原始处理器
                mock_original.assert_called_once()
                
                # 错误应该被添加到历史
                assert len(handler.error_history) > 0
            
        finally:
            sys.excepthook = original_hook


class TestErrorHandlerIntegration:
    """错误处理器集成测试"""
    
    def test_full_error_flow(self):
        """测试完整错误流程"""
        mock_logger = Mock()
        handler = ErrorHandler(mock_logger)
        
        # 1. 触发一个错误
        error = FileNotFoundError("config.json 不存在")
        
        try:
            handler.handle_error(error, operation="加载配置")
        except AIError as e:
            # 2. 检查错误
            assert e.error_code == ErrorCode.FILE_NOT_FOUND
            assert "config.json" in e.message
            
            # 3. 检查统计
            stats = handler.get_error_stats()
            assert stats["total_errors"] == 1
            assert stats["error_counts"]["E0003"] == 1
            
            # 4. 检查历史
            recent = handler.get_recent_errors()
            assert len(recent) == 1
            assert recent[0]["code"] == "E0003"
            
            # 5. 检查日志
            mock_logger.error.assert_called_once()
            
            # 6. 清空历史
            handler.clear_history()
            
            stats = handler.get_error_stats()
            assert stats["total_errors"] == 0
    
    def test_multiple_error_types(self):
        """测试多种错误类型"""
        handler = ErrorHandler()
        
        errors = [
            (FileNotFoundError("文件1"), ErrorCode.FILE_NOT_FOUND),
            (PermissionError("权限1"), ErrorCode.PERMISSION_ERROR),
            (ConnectionError("网络1"), ErrorCode.NETWORK_ERROR),
            (FileNotFoundError("文件2"), ErrorCode.FILE_NOT_FOUND)
        ]
        
        for error, _ in errors:
            try:
                handler.handle_error(error, raise_exception=False)
            except AIError:
                pass
        
        stats = handler.get_error_stats()
        
        # 检查计数
        assert stats["total_errors"] == 4
        assert stats["error_counts"]["E0003"] == 2  # FILE_NOT_FOUND
        assert stats["error_counts"]["E0004"] == 1  # PERMISSION_ERROR
        assert stats["error_counts"]["E0005"] == 1  # NETWORK_ERROR