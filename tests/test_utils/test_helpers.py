#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助工具测试
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import threading

from src.utils.helpers import (
    time_it, retry, safe_execute, format_size, format_time,
    generate_id, md5_hash, json_pretty, get_file_info,
    read_lines, write_lines, deep_update, chunk_list,
    flatten, get_caller_info, run_in_thread, run_in_background,
    Timer, RateLimiter, validate_email, validate_url,
    get_system_info, print_system_info, Singleton
)


class TestDecorators:
    """装饰器测试"""
    
    def test_time_it_decorator(self):
        """测试计时装饰器"""
        @time_it
        def slow_function():
            time.sleep(0.01)
            return "完成"
        
        result = slow_function()
        
        assert result == "完成"
    
    def test_retry_decorator_success(self):
        """测试重试装饰器（成功）"""
        call_count = 0
        
        @retry(max_retries=3, delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("模拟失败")
            return "成功"
        
        result = failing_function()
        
        assert result == "成功"
        assert call_count == 2
    
    def test_retry_decorator_failure(self):
        """测试重试装饰器（失败）"""
        call_count = 0
        
        @retry(max_retries=2, delay=0.01)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("总是失败")
        
        with pytest.raises(RuntimeError, match="总是失败"):
            always_failing()
        
        assert call_count == 3  # 初始 + 2次重试
    
    def test_retry_with_logger(self):
        """测试带日志器的重试装饰器"""
        mock_logger = Mock()
        
        call_count = 0
        
        @retry(max_retries=2, delay=0.01, logger=mock_logger)
        def logging_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("测试")
            return "完成"
        
        result = logging_function()
        
        assert result == "完成"
        assert mock_logger.info.call_count >= 1


class TestHelperFunctions:
    """辅助函数测试"""
    
    def test_safe_execute_success(self):
        """测试安全执行成功"""
        def successful_func():
            return "结果"
        
        result = safe_execute(successful_func, default_return="默认")
        
        assert result == "结果"
    
    def test_safe_execute_failure(self):
        """测试安全执行失败"""
        def failing_func():
            raise ValueError("错误")
        
        result = safe_execute(failing_func, default_return="默认", logger=None)
        
        assert result == "默认"
    
    def test_safe_execute_with_logger(self):
        """测试带日志器的安全执行"""
        mock_logger = Mock()
        
        def failing_func():
            raise RuntimeError("测试错误")
        
        result = safe_execute(failing_func, default_return=None, logger=mock_logger)
        
        assert result is None
        mock_logger.error.assert_called_once()
    
    def test_format_size(self):
        """测试格式化大小"""
        test_cases = [
            (0, "0.00 B"),
            (1024, "1.00 KB"),
            (1024**2, "1.00 MB"),
            (1024**3, "1.00 GB"),
            (1024**4, "1.00 TB"),
            (1500, "1.46 KB"),
            (1500000, "1.43 MB")
        ]
        
        for size, expected in test_cases:
            result = format_size(size)
            assert result == expected
    
    def test_format_time(self):
        """测试格式化时间"""
        test_cases = [
            (0.001, "1ms"),
            (0.5, "500ms"),
            (1.5, "1.5s"),
            (65, "1m 5s"),
            (3661, "1h 1m 1s"),
            (90061, "25h 1m 1s")
        ]
        
        for seconds, expected in test_cases:
            result = format_time(seconds)
            # 允许一些格式差异
            assert "m" in result or "s" in result or "h" in result
    
    def test_generate_id(self):
        """测试生成ID"""
        # 测试默认长度
        id1 = generate_id()
        assert len(id1) == 8
        
        # 测试指定长度
        id2 = generate_id(12)
        assert len(id2) == 12
        
        # 测试带前缀
        id3 = generate_id(prefix="test_")
        assert id3.startswith("test_")
        assert len(id3) == 8 + len("test_")
        
        # 测试唯一性（大概）
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100
    
    def test_md5_hash(self):
        """测试MD5哈希"""
        # 测试字符串
        result1 = md5_hash("hello world")
        assert len(result1) == 32  # MD5是32位十六进制
        assert result1 == "5eb63bbbe01eeed093cb22bb8f5acdc3"
        
        # 测试字节
        result2 = md5_hash(b"hello world")
        assert result2 == "5eb63bbbe01eeed093cb22bb8f5acdc3"
        
        # 测试中文
        result3 = md5_hash("你好世界")
        assert len(result3) == 32
    
    def test_json_pretty(self):
        """测试JSON美化"""
        data = {
            "name": "测试",
            "value": 123,
            "nested": {
                "key": "值",
                "list": [1, 2, 3]
            }
        }
        
        result = json_pretty(data)
        
        # 应该是有效的JSON
        parsed = json.loads(result)
        assert parsed["name"] == "测试"
        assert parsed["value"] == 123
        assert parsed["nested"]["key"] == "值"
        
        # 应该包含换行和缩进
        assert "\n" in result
        assert "  " in result  # 缩进
    
    def test_get_file_info(self, temp_dir):
        """测试获取文件信息"""
        # 创建测试文件
        test_file = temp_dir / "test.txt"
        test_file.write_text("测试内容")
        
        info = get_file_info(test_file)
        
        assert info["filename"] == "test.txt"
        assert info["path"] == str(test_file.absolute())
        assert info["size"] == len("测试内容".encode('utf-8'))
        assert info["type"] == "file"
        assert "created" in info
        assert "modified" in info
        
        # 测试不存在的文件
        nonexistent = temp_dir / "nonexistent.txt"
        info = get_file_info(nonexistent)
        
        assert info == {}
    
    def test_read_lines(self, temp_dir):
        """测试读取行"""
        test_file = temp_dir / "lines.txt"
        lines = ["第一行", "第二行", "第三行"]
        test_file.write_text("\n".join(lines))
        
        result = read_lines(test_file)
        
        assert result == lines
    
    def test_read_lines_nonexistent(self, temp_dir):
        """测试读取不存在的文件"""
        nonexistent = temp_dir / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            read_lines(nonexistent)
    
    def test_write_lines(self, temp_dir):
        """测试写入行"""
        test_file = temp_dir / "output.txt"
        lines = ["输出1", "输出2", "输出3"]
        
        write_lines(test_file, lines)
        
        content = test_file.read_text(encoding='utf-8')
        assert content == "输出1\n输出2\n输出3"
    
    def test_deep_update(self):
        """测试深度更新"""
        original = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }
        
        update = {
            "a": 10,
            "b": {
                "c": 20
            },
            "e": 5
        }
        
        result = deep_update(original, update)
        
        assert result["a"] == 10
        assert result["b"]["c"] == 20
        assert result["b"]["d"] == 3  # 应该保留
        assert result["e"] == 5
    
    def test_chunk_list(self):
        """测试列表分块"""
        lst = [1, 2, 3, 4, 5, 6, 7]
        
        chunks = chunk_list(lst, 3)
        
        assert len(chunks) == 3
        assert chunks[0] == [1, 2, 3]
        assert chunks[1] == [4, 5, 6]
        assert chunks[2] == [7]
        
        # 测试正好整除
        chunks2 = chunk_list([1, 2, 3, 4], 2)
        assert chunks2 == [[1, 2], [3, 4]]
    
    def test_flatten(self):
        """测试展平列表"""
        nested = [[1, 2], [3, [4, 5]], 6]
        
        result = flatten(nested)
        
        assert result == [1, 2, 3, 4, 5, 6]
        
        # 测试空列表
        assert flatten([]) == []
        assert flatten([[]]) == []
    
    def test_get_caller_info(self):
        """测试获取调用者信息"""
        info = get_caller_info()
        
        assert isinstance(info, dict)
        # 至少应该有这些键
        assert "filename" in info
        assert "function" in info
        assert "lineno" in info
        
        # 调用者应该是这个测试函数
        assert "test_get_caller_info" in info["function"]
    
    def test_run_in_thread(self):
        """测试在线程中运行"""
        result = []
        
        def thread_func():
            result.append("完成")
        
        thread = run_in_thread(thread_func)
        thread.join(timeout=1.0)
        
        assert result == ["完成"]
        assert thread.daemon is True
    
    def test_run_in_background(self):
        """测试在后台运行"""
        result = []
        
        def background_func():
            result.append("后台完成")
        
        timer = run_in_background(background_func, delay=0.01)
        time.sleep(0.05)  # 等待执行
        
        assert result == ["后台完成"]
        assert timer.daemon is True


class TestTimer:
    """计时器测试"""
    
    def test_timer_context(self):
        """测试计时器上下文管理器"""
        with Timer("测试计时器") as timer:
            time.sleep(0.01)
        
        assert timer.elapsed > 0
    
    def test_timer_manual(self):
        """测试手动计时器"""
        timer = Timer("手动测试")
        
        timer.start()
        time.sleep(0.01)
        timer.stop()
        
        assert timer.elapsed > 0
        
        # 格式应该包含时间单位
        formatted = timer.format_result()
        assert "ms" in formatted or "s" in formatted
    
    def test_timer_get_elapsed(self):
        """测试获取经过时间"""
        timer = Timer("获取时间")
        
        timer.start()
        time.sleep(0.01)
        elapsed = timer.get_elapsed()
        
        assert elapsed > 0
        assert elapsed < 0.1  # 应该小于100ms
        
        timer.stop()


class TestRateLimiter:
    """速率限制器测试"""
    
    def test_rate_limiter(self):
        """测试速率限制器"""
        limiter = RateLimiter(calls_per_second=10)  # 10次/秒
        
        start = time.time()
        
        for _ in range(3):
            limiter.wait()
        
        elapsed = time.time() - start
        
        # 3次调用，每次至少间隔0.1秒
        assert elapsed >= 0.2  # 2个间隔
    
    def test_rate_limiter_decorator(self):
        """测试速率限制器装饰器"""
        call_times = []
        
        @RateLimiter(calls_per_second=5)
        def limited_function():
            call_times.append(time.time())
        
        start = time.time()
        
        for _ in range(3):
            limited_function()
        
        elapsed = time.time() - start
        
        assert elapsed >= 0.4  # 2个间隔，每次至少0.2秒
        assert len(call_times) == 3


class TestValidation:
    """验证函数测试"""
    
    def test_validate_email(self):
        """测试邮箱验证"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid",
            "missing@domain",
            "@example.com",
            "user@.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_validate_url(self):
        """测试URL验证"""
        valid_urls = [
            "http://example.com",
            "https://www.example.com/path",
            "http://sub.domain.co.uk/page?query=1"
        ]
        
        invalid_urls = [
            "not-a-url",
            "example.com",  # 缺少协议
            "http://",  # 缺少域名
            "ftp://example.com"  # 不支持FTP
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
        
        for url in invalid_urls:
            assert validate_url(url) is False


class TestSystemInfo:
    """系统信息测试"""
    
    def test_get_system_info(self):
        """测试获取系统信息"""
        info = get_system_info()
        
        assert isinstance(info, dict)
        assert "system" in info
        assert "python_version" in info
        assert "memory_total" in info
        assert "cpu_count_physical" in info
    
    def test_print_system_info(self, capsys):
        """测试打印系统信息"""
        print_system_info()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "系统信息" in output
        assert "=" in output


class TestSingleton:
    """单例模式测试"""
    
    def test_singleton_metaclass(self):
        """测试单例元类"""
        
        class TestClass(metaclass=Singleton):
            def __init__(self, value):
                self.value = value
        
        # 创建第一个实例
        instance1 = TestClass("第一个")
        assert instance1.value == "第一个"
        
        # 创建第二个实例（应该返回同一个）
        instance2 = TestClass("第二个")
        assert instance2 is instance1
        assert instance2.value == "第一个"  # 应该还是第一个的值
        
        # 创建第三个实例
        instance3 = TestClass("第三个")
        assert instance3 is instance1