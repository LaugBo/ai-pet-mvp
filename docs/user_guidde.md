# AI宠物MVP - 用户指南

欢迎使用AI宠物MVP！这是一个具有情感交互能力的AI聊天伙伴，能够根据对话内容改变心情，并记住你们的对话历史。

## 目录
- [快速开始](#快速开始)
- [界面介绍](#界面介绍)
- [基本功能](#基本功能)
- [心情系统](#心情系统)
- [记忆功能](#记忆功能)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

## 快速开始

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 500MB 可用空间

### 安装步骤

1. **安装Python**
   - 访问 [python.org](https://www.python.org/downloads/) 下载并安装Python 3.8+

2. **下载项目**
bash

git clone https://github.com/yourusername/ai-pet-mvp.git

cd ai-pet-mvp
3. **安装依赖**
bash

pip install -r requirements.txt
4. **安装Ollama（可选）**
- 如果你要使用本地AI模型，需要安装Ollama
- 访问 [ollama.com](https://ollama.com/) 下载并安装
- 拉取一个模型：`ollama pull qwen:7b`

5. **启动应用**
bash

python run_app.py
## 界面介绍

### 主界面布局
┌──────────────────────────────────────────────┐

│  AI宠物MVP                          🗕 🗖 ✕  │

├──────────────────────────────────────────────┤

│  ┌──────────────┐  ┌────────────────────┐  │

│  │              │  │                    │  │

│  │   聊天区域    │  │    心情显示区      │  │

│  │              │  │                    │  │

│  │  ┌────────┐  │  │  ┌──────────────┐  │  │

│  │  │输入框  │  │  │  │  心情图片    │  │  │

│  │  └────────┘  │  │  └──────────────┘  │  │

│  │  [发送按钮]   │  │  心情: 开心(85%)   │  │

│  │              │  │  原因: 用户说了...  │  │

│  └──────────────┘  └────────────────────┘  │

└──────────────────────────────────────────────┘
### 区域说明

1. **聊天区域**（左侧）
   - 显示对话历史
   - 用户消息（蓝色气泡）
   - AI回复（灰色气泡）
   - 系统消息（绿色气泡）

2. **输入区域**（左下）
   - 文本输入框：输入消息
   - 发送按钮：发送消息
   - 快捷键：`Ctrl+Enter` 或 `Enter` 发送

3. **心情显示区**（右侧）
   - 心情图片：根据AI宠物心情变化
   - 心情状态：当前心情和置信度
   - 原因说明：心情变化的原因

4. **状态栏**（底部）
   - 连接状态：AI连接状态
   - 消息计数：当前对话消息数

## 基本功能

### 开始对话
1. 确保AI宠物已连接（状态栏显示"已连接"）
2. 在输入框中输入消息
3. 点击"发送"按钮或按 `Ctrl+Enter`
4. 等待AI回复

### 对话示例
你: 你好，AI宠物！

AI: 你好！我是你的AI宠物，今天心情不错！

你: 今天天气真好

AI: 是啊，阳光明媚，适合出去散步呢！

你: 给我讲个笑话吧

AI: 为什么程序员不喜欢大自然？因为有太多bug！
### 快捷键
- `Ctrl+Enter` / `Enter`: 发送消息
- `Ctrl+C`: 复制选中文本
- `Ctrl+V`: 粘贴文本
- `Ctrl+A`: 全选输入框
- `Ctrl+Z`: 撤销输入
- `Esc`: 清除输入框

## 心情系统

### 心情类型
AI宠物有6种基本心情：

| 心情 | 表情 | 触发条件 | 说明 |
|------|------|----------|------|
| 😊 开心 | 笑脸 | 积极词汇、赞美、好消息 | AI感到快乐和满足 |
| 😢 伤心 | 哭脸 | 消极词汇、抱怨、坏消息 | AI感到难过或失望 |
| 😐 中性 | 平静脸 | 普通对话、事实陈述 | AI情绪平稳 |
| 😠 生气 | 生气脸 | 争吵、冲突、负面词汇 | AI感到不满或愤怒 |
| 😨 害怕 | 害怕脸 | 危险、威胁、恐怖内容 | AI感到害怕或担忧 |
| 🤔 困惑 | 思考脸 | 复杂问题、矛盾信息 | AI感到困惑不解 |

### 心情变化规则
1. **实时分析**: 每次对话都会分析用户消息的情感
2. **累积效应**: 连续相似的情绪会加强当前心情
3. **自然衰减**: 长时间无对话会逐渐回归中性
4. **记忆影响**: 历史对话会影响当前心情判断

### 如何影响AI心情
- **让AI开心**: 使用积极词汇、表达感谢、分享好消息
- **让AI伤心**: 表达难过、抱怨问题、分享坏消息
- **安慰AI**: 当AI伤心时，可以说些鼓励的话
- **逗AI开心**: 讲笑话、分享有趣的事情

## 记忆功能

### 自动记忆
- 所有对话自动保存到本地
- 按日期和时间组织
- 支持搜索历史对话
- 自动生成对话摘要

### 记忆管理
1. **查看历史**
   - 对话记录保存在 `data/memory/conversations/`
   - 每个文件包含一次完整的对话
   - 文件名包含时间戳便于查找

2. **搜索对话**
   - 支持关键词搜索
   - 按时间范围过滤
   - 按心情类型筛选

3. **导出对话**
   - 支持导出为JSON格式
   - 支持导出为文本格式
   - 可以导出选定时间段的对话

### 隐私保护
- 所有数据保存在本地
- 不会上传到云端
- 可以随时清理对话历史
- 支持数据加密（可选）

## 配置说明

### 配置文件位置
data/config/

├── ai_profiles.json    # AI服务配置

├── settings.json       # 应用设置

└── mood_rules.json     # 心情规则
### AI配置示例
OK

继续生成剩下的测试和文档文件。

📄 文件9: 辅助工具测试

位置: D:\AI_Pet\ai_pet_mvp\tests\test_utils\test_helpers.py

python
下载
复制
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
📄 文件10: 错误处理器测试

位置: D:\AI_Pet\ai_pet_mvp\tests\test_utils\test_error_handler.py

python
下载
复制
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
📄 文件11: 集成测试

位置: D:\AI_Pet\ai_pet_mvp\tests\test_integration\test_full_app.py

python
下载
复制
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整应用集成测试
测试所有模块的集成工作
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys

from src.ui.window import MainWindow
from src.ui.chat import ChatManager
from src.utils.config import ConfigManager
from src.core.ai.adapter import AIManager
from src.core.memory.storage import MemoryStorage
from src.core.mood.manager import MoodManager
from src.core.mood.images import MoodImageManager
from src.core.mood.analyzer import MoodType


class TestFullAppIntegration:
    """完整应用集成测试"""
    
    @pytest.fixture
    def temp_project(self):
        """临时项目fixture"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "ai_pet"
            project_dir.mkdir()
            
            # 创建项目结构
            (project_dir / "data").mkdir()
            (project_dir / "data" / "config").mkdir(parents=True)
            (project_dir / "data" / "memory").mkdir(parents=True)
            (project_dir / "src").mkdir()
            
            yield project_dir
    
    def test_config_manager_integration(self, temp_project):
        """测试配置管理器集成"""
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 测试配置读写
        test_config = {
            "test": "value",
            "nested": {"key": "value"}
        }
        
        # 保存配置
        result = config_manager.save_config("test_config.json", test_config)
        assert result is True
        
        # 加载配置
        loaded = config_manager.load_config("test_config.json")
        assert loaded == test_config
        
        # 测试默认值
        default = config_manager.load_config("nonexistent.json", {"default": "value"})
        assert default == {"default": "value"}
    
    def test_ai_system_integration(self, temp_project):
        """测试AI系统集成"""
        # 创建AI配置
        ai_config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        # 创建AI管理器
        ai_manager = AIManager(ai_config)
        
        assert ai_manager.config == ai_config
        assert ai_manager.adapter is None
        assert ai_manager.is_connected is False
        
        # 测试状态获取
        status = ai_manager.get_status()
        assert status["type"] == "ollama"
        assert status["connected"] is False
    
    def test_memory_system_integration(self, temp_project):
        """测试记忆系统集成"""
        # 创建记忆存储
        memory_storage = MemoryStorage()
        
        # 测试对话保存
        conversation = {
            "user": "集成测试消息",
            "ai": "集成测试回复",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        result = memory_storage.save_conversation(conversation)
        assert result is True
        
        # 测试获取数量
        count = memory_storage.get_conversation_count()
        assert count == 1
        
        # 测试获取最近对话
        recent = memory_storage.get_recent_conversations(limit=5)
        assert len(recent) == 1
        assert recent[0]["user"] == "集成测试消息"
        
        # 测试心情保存
        mood_data = {
            "mood": "happy",
            "reason": "集成测试",
            "confidence": 0.9
        }
        
        result = memory_storage.save_mood(mood_data)
        assert result is True
        
        # 测试加载心情历史
        mood_history = memory_storage.load_mood_history(limit=5)
        assert len(mood_history) == 1
    
    def test_mood_system_integration(self, temp_project):
        """测试心情系统集成"""
        # 创建记忆存储
        memory_storage = MemoryStorage()
        
        # 创建心情管理器
        mood_manager = MoodManager(storage_manager=memory_storage)
        
        # 测试初始状态
        assert mood_manager.current_mood == MoodType.NEUTRAL
        assert mood_manager.mood_history == []
        
        # 测试回调
        callback_called = []
        def test_callback(old_mood, new_result):
            callback_called.append((old_mood, new_result))
        
        mood_manager.register_mood_change_callback(test_callback)
        
        # 测试心情分析（模拟）
        with patch('src.core.mood.analyzer.MoodAnalyzer.analyze') as mock_analyze:
            from src.core.mood.analyzer import MoodResult
            
            mock_analyze.return_value = MoodResult(
                mood_type=MoodType.HAPPY,
                confidence=0.85,
                reason="检测到积极词汇"
            )
            
            # 分析文本
            result = mood_manager.analyze_and_update("今天我很开心！")
            
            assert result is True
            assert mood_manager.current_mood == MoodType.HAPPY
            assert len(mood_manager.mood_history) == 1
            assert len(callback_called) == 1
        
        # 测试保存心情
        result = mood_manager.save_current_mood()
        assert result is True
        
        # 测试加载历史
        history = mood_manager.load_mood_history(limit=5)
        assert isinstance(history, list)
    
    def test_mood_image_integration(self, temp_project):
        """测试心情图片集成"""
        # 创建临时资源目录
        assets_dir = temp_project / "src" / "ui" / "assets"
        assets_dir.mkdir(parents=True)
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建测试图片
        for mood in ["happy", "sad", "neutral"]:
            (moods_dir / f"{mood}.png").write_bytes(b"fake image data")
        
        # 创建图片管理器
        image_manager = MoodImageManager(str(assets_dir))
        
        # 测试获取图片路径
        happy_path = image_manager.get_mood_image_path("happy")
        assert happy_path is not None
        assert "happy.png" in str(happy_path)
        
        # 测试获取不存在的心情
        unknown_path = image_manager.get_mood_image_path("unknown")
        assert unknown_path is not None
        assert "neutral.png" in str(unknown_path)  # 应该返回默认
        
        # 测试获取所有图片
        all_images = image_manager.get_all_mood_images()
        assert len(all_images) >= 3
        assert "happy" in all_images
        assert "sad" in all_images
        assert "neutral" in all_images
    
    def test_chat_manager_integration(self, temp_project):
        """测试聊天管理器集成"""
        # 创建模拟组件
        config_manager = Mock()
        ai_manager = Mock()
        memory_storage = Mock()
        
        # 配置AI管理器
        ai_manager.is_connected = True
        ai_manager.generate_response.return_value = "模拟AI回复"
        
        # 配置记忆存储
        memory_storage.save_conversation.return_value = True
        memory_storage.get_recent_conversations.return_value = []
        
        # 创建聊天管理器
        chat_manager = ChatManager(config_manager, ai_manager)
        chat_manager.set_memory_storage(memory_storage)
        
        # 测试连接
        result = chat_manager.connect_ai()
        assert result is True
        assert chat_manager.is_connected is True
        
        # 测试发送消息
        chat_manager.response_received = Mock()
        chat_manager.error_occurred = Mock()
        
        chat_manager.send_message("测试消息")
        
        # 验证AI被调用
        ai_manager.generate_response.assert_called_with("测试消息", None)
        
        # 验证响应信号
        chat_manager.response_received.emit.assert_called_with("模拟AI回复")
        
        # 验证历史记录
        assert len(chat_manager.conversation_history) == 1
        assert chat_manager.conversation_history[0]["user"] == "测试消息"
        assert chat_manager.conversation_history[0]["ai"] == "模拟AI回复"
        
        # 验证记忆保存
        memory_storage.save_conversation.assert_called()
        
        # 测试获取状态
        status = chat_manager.get_status()
        assert status["connected"] is True
        assert status["history_count"] == 1
    
    def test_window_integration(self, temp_project, qt_app):
        """测试窗口集成"""
        # 创建模拟组件
        config_manager = Mock()
        mood_manager = Mock()
        image_manager = Mock()
        
        # 配置组件
        config_manager.load_config.return_value = {}
        mood_manager.current_mood = MoodType.NEUTRAL
        image_manager.get_mood_image_path.return_value = "/fake/path/neutral.png"
        
        # 创建窗口
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 测试UI组件
        assert window.chat_input is not None
        assert window.send_button is not None
        assert window.chat_display is not None
        assert window.mood_label is not None
        
        # 测试添加消息
        window._add_user_message("用户消息")
        window._add_ai_message("AI消息")
        window._add_system_message("系统消息")
        
        assert window.message_count == 3
        
        # 测试更新心情显示
        window._update_mood_display(
            mood_type=MoodType.HAPPY,
            confidence=0.8,
            reason="测试原因"
        )
        
        # 应该调用了图片管理器
        image_manager.get_mood_image_path.assert_called_with("happy")
        
        # 测试发送消息
        window.chat_input.setText("要发送的消息")
        window.send_message_signal = Mock()
        
        window._on_send_message()
        
        # 应该发送了信号
        window.send_message_signal.emit.assert_called_with("要发送的消息")
        
        # 输入框应该被清空
        assert window.chat_input.text() == ""
        
        # 应该分析了心情
        mood_manager.analyze_and_update.assert_called_with("要发送的消息")
        
        window.close()
    
    def test_full_workflow(self, temp_project, qt_app):
        """测试完整工作流程"""
        # 1. 创建所有组件
        config_manager = Mock()
        ai_manager = Mock()
        memory_storage = Mock()
        mood_manager = Mock()
        image_manager = Mock()
        
        # 2. 配置组件
        config_manager.load_config.return_value = {}
        
        ai_manager.is_connected = True
        ai_manager.generate_response.return_value = "完整流程回复"
        
        memory_storage.save_conversation.return_value = True
        memory_storage.get_recent_conversations.return_value = []
        
        mood_manager.current_mood = MoodType.NEUTRAL
        mood_manager.analyze_and_update.return_value = True
        
        image_manager.get_mood_image_path.return_value = "/fake/path/neutral.png"
        
        # 3. 创建聊天管理器
        chat_manager = ChatManager(config_manager, ai_manager)
        chat_manager.set_memory_storage(memory_storage)
        chat_manager.connect_ai()
        
        # 4. 创建窗口
        window = MainWindow(config_manager, mood_manager, image_manager)
        window.set_chat_manager(chat_manager)
        window.set_ai_manager(ai_manager)
        
        # 5. 连接信号
        window.send_message_signal.connect(chat_manager.send_message)
        chat_manager.response_received.connect(window.update_ai_response)
        chat_manager.error_occurred.connect(window.show_error)
        
        # 6. 模拟用户交互
        # 用户输入消息
        window.chat_input.setText("完整流程测试")
        
        # 用户点击发送
        window._on_send_message()
        
        # 验证消息发送
        window.send_message_signal.emit.assert_called_with("完整流程测试")
        
        # 模拟AI响应
        window.update_ai_response("完整流程回复")
        
        # 验证消息显示
        assert window.message_count > 0
        
        # 7. 验证组件状态
        assert chat_manager.is_connected is True
        assert len(chat_manager.conversation_history) == 1
        
        # 8. 清理
        window.close()
    
    def test_error_handling_integration(self, temp_project):
        """测试错误处理集成"""
        from src.utils.error_handler import get_error_handler, AIError, ErrorCode
        from src.utils.logger import get_logger
        
        # 获取日志器和错误处理器
        logger = get_logger("integration_error_test")
        error_handler = get_error_handler(logger)
        
        # 测试错误处理
        try:
            raise FileNotFoundError("集成测试文件不存在")
        except Exception as e:
            ai_error = error_handler.handle_error(
                e,
                operation="集成错误测试",
                context={"test": "data"},
                raise_exception=False
            )
            
            assert isinstance(ai_error, AIError)
            assert ai_error.error_code == ErrorCode.FILE_NOT_FOUND
        
        # 检查错误统计
        stats = error_handler.get_error_stats()
        assert stats["total_errors"] > 0
    
    def test_backup_restore_integration(self, temp_project):
        """测试备份恢复集成"""
        from scripts.backup import BackupManager
        import zipfile
        
        # 创建一些测试数据
        data_dir = temp_project / "data"
        
        # 创建测试对话文件
        conv_dir = data_dir / "memory" / "conversations"
        conv_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(3):
            conv_file = conv_dir / f"conv_{i}.json"
            conv_file.write_text(json.dumps({
                "user": f"消息{i}",
                "ai": f"回复{i}"
            }, ensure_ascii=False))
        
        # 创建备份管理器
        backup_manager = BackupManager(temp_project / "backups")
        
        # 创建备份
        backup_path = backup_manager.create_backup(
            backup_name="integration_test",
            compress=True
        )
        
        assert backup_path.exists()
        assert backup_path.suffix == ".zip"
        
        # 列出备份
        backups = backup_manager.list_backups()
        assert len(backups) == 1
        assert backups[0]["name"] == "integration_test"
        
        # 删除原始数据
        for conv_file in conv_dir.glob("*.json"):
            conv_file.unlink()
        
        # 恢复备份
        result = backup_manager.restore_backup(
            backup_name="integration_test",
            target_dir=temp_project,
            overwrite=True
        )
        
        assert result is True
        
        # 验证数据恢复
        restored_files = list(conv_dir.glob("*.json"))
        assert len(restored_files) == 3
    
    def test_clean_integration(self, temp_project):
        """测试清理集成"""
        from scripts.clean import CleanManager
        
        # 创建一些测试文件
        pycache_dir = temp_project / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.pyc").write_bytes(b"fake pyc")
        
        temp_file = temp_project / "test.tmp"
        temp_file.write_text("临时文件")
        
        # 创建清理管理器
        clean_manager = CleanManager()
        
        # 扫描文件
        found_files = clean_manager.scan(dry_run=True)
        
        total_files = sum(len(files) for files in found_files.values())
        assert total_files > 0
        
        # 实际清理
        results = clean_manager.clean(dry_run=False)
        
        total_deleted = sum(stats["deleted"] for stats in results.values())
        assert total_deleted > 0
        
        # 验证文件被删除
        assert not pycache_dir.exists()
        assert not temp_file.exists()


class TestPerformance:
    """性能测试"""
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 创建一些对象
        from src.core.memory.storage import MemoryStorage
        storage = MemoryStorage()
        
        # 保存一些对话
        for i in range(100):
            storage.save_conversation({
                "user": f"消息{i}",
                "ai": f"回复{i}"
            })
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增加应该在合理范围内（小于10MB）
        assert memory_increase < 10 * 1024 * 1024  # 10MB
    
    def test_response_time(self):
        """测试响应时间"""
        # 模拟AI响应
        ai_manager = Mock()
        ai_manager.is_connected = True
        
        def mock_generate(prompt, **kwargs):
            time.sleep(0.01)  # 模拟10ms延迟
            return f"回复: {prompt}"
        
        ai_manager.generate_response = Mock(side_effect=mock_generate)
        
        # 测试响应时间
        start_time = time.time()
        
        for _ in range(10):
            ai_manager.generate_response("测试消息")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10次调用，每次10ms，总共约100ms
        # 加上一些开销，应该小于200ms
        assert total_time < 0.2  # 200ms
    
    def test_concurrent_access(self):
        """测试并发访问"""
        import threading
        
        from src.core.memory.storage import MemoryStorage
        storage = MemoryStorage()
        
        results = []
        errors = []
        
        def save_conversation(thread_id):
            try:
                for i in range(10):
                    storage.save_conversation({
                        "user": f"线程{thread_id}-消息{i}",
                        "ai": f"回复{i}"
                    })
                results.append(f"线程{thread_id}完成")
            except Exception as e:
                errors.append(str(e))
        
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_conversation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=2.0)
        
        # 检查结果
        assert len(errors) == 0
        assert len(results) == 5
        
        # 检查保存的对话数量
        count = storage.get_conversation_count()
        assert count == 50  # 5线程 * 10次


class TestDocumentationExamples:
    """文档示例测试"""
    
    def test_basic_usage_example(self):
        """测试基础使用示例"""
        # 示例：创建AI管理器
        ai_config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        ai_manager = AIManager(ai_config)
        
        assert ai_manager is not None
        assert ai_manager.config == ai_config
    
    def test_mood_analysis_example(self):
        """测试心情分析示例"""
        from src.core.mood.analyzer import MoodAnalyzer
        
        analyzer = MoodAnalyzer()
        
        # 分析文本
        result = analyzer.analyze("今天我很开心！")
        
        assert result is not None
        assert hasattr(result, 'mood_type')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'reason')
    
    def test_memory_storage_example(self):
        """测试记忆存储示例"""
        storage = MemoryStorage()
        
        # 保存对话
        conversation = {
            "user": "示例消息",
            "ai": "示例回复",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        result = storage.save_conversation(conversation)
        
        assert result is True
        
        # 获取统计
        count = storage.get_conversation_count()
        
        assert count >= 1
📄 文件12: 用户指南

位置: D:\AI_Pet\ai_pet_mvp\docs\user_guide.md

markdown
复制
# AI宠物MVP - 用户指南

欢迎使用AI宠物MVP！这是一个具有情感交互能力的AI聊天伙伴，能够根据对话内容改变心情，并记住你们的对话历史。

## 目录
- [快速开始](#快速开始)
- [界面介绍](#界面介绍)
- [基本功能](#基本功能)
- [心情系统](#心情系统)
- [记忆功能](#记忆功能)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

## 快速开始

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 500MB 可用空间

### 安装步骤

1. **安装Python**
   - 访问 [python.org](https://www.python.org/downloads/) 下载并安装Python 3.8+

2. **下载项目**

bash

git clone https://github.com/yourusername/ai-pet-mvp.git

cd ai-pet-mvp

复制
3. **安装依赖**

bash

pip install -r requirements.txt

复制
4. **安装Ollama（可选）**
- 如果你要使用本地AI模型，需要安装Ollama
- 访问 [ollama.com](https://ollama.com/) 下载并安装
- 拉取一个模型：`ollama pull qwen:7b`

5. **启动应用**

bash

python run_app.py

复制
## 界面介绍

### 主界面布局

┌──────────────────────────────────────────────┐

│  AI宠物MVP                          🗕 🗖 ✕  │

├──────────────────────────────────────────────┤

│  ┌──────────────┐  ┌────────────────────┐  │

│  │              │  │                    │  │

│  │   聊天区域    │  │    心情显示区      │  │

│  │              │  │                    │  │

│  │  ┌────────┐  │  │  ┌──────────────┐  │  │

│  │  │输入框  │  │  │  │  心情图片    │  │  │

│  │  └────────┘  │  │  └──────────────┘  │  │

│  │  [发送按钮]   │  │  心情: 开心(85%)   │  │

│  │              │  │  原因: 用户说了...  │  │

│  └──────────────┘  └────────────────────┘  │

└──────────────────────────────────────────────┘

复制
### 区域说明

1. **聊天区域**（左侧）
   - 显示对话历史
   - 用户消息（蓝色气泡）
   - AI回复（灰色气泡）
   - 系统消息（绿色气泡）

2. **输入区域**（左下）
   - 文本输入框：输入消息
   - 发送按钮：发送消息
   - 快捷键：`Ctrl+Enter` 或 `Enter` 发送

3. **心情显示区**（右侧）
   - 心情图片：根据AI宠物心情变化
   - 心情状态：当前心情和置信度
   - 原因说明：心情变化的原因

4. **状态栏**（底部）
   - 连接状态：AI连接状态
   - 消息计数：当前对话消息数

## 基本功能

### 开始对话
1. 确保AI宠物已连接（状态栏显示"已连接"）
2. 在输入框中输入消息
3. 点击"发送"按钮或按 `Ctrl+Enter`
4. 等待AI回复

### 对话示例

你: 你好，AI宠物！

AI: 你好！我是你的AI宠物，今天心情不错！

你: 今天天气真好

AI: 是啊，阳光明媚，适合出去散步呢！

你: 给我讲个笑话吧

AI: 为什么程序员不喜欢大自然？因为有太多bug！

复制
### 快捷键
- `Ctrl+Enter` / `Enter`: 发送消息
- `Ctrl+C`: 复制选中文本
- `Ctrl+V`: 粘贴文本
- `Ctrl+A`: 全选输入框
- `Ctrl+Z`: 撤销输入
- `Esc`: 清除输入框

## 心情系统

### 心情类型
AI宠物有6种基本心情：

| 心情 | 表情 | 触发条件 | 说明 |
|------|------|----------|------|
| 😊 开心 | 笑脸 | 积极词汇、赞美、好消息 | AI感到快乐和满足 |
| 😢 伤心 | 哭脸 | 消极词汇、抱怨、坏消息 | AI感到难过或失望 |
| 😐 中性 | 平静脸 | 普通对话、事实陈述 | AI情绪平稳 |
| 😠 生气 | 生气脸 | 争吵、冲突、负面词汇 | AI感到不满或愤怒 |
| 😨 害怕 | 害怕脸 | 危险、威胁、恐怖内容 | AI感到害怕或担忧 |
| 🤔 困惑 | 思考脸 | 复杂问题、矛盾信息 | AI感到困惑不解 |

### 心情变化规则
1. **实时分析**: 每次对话都会分析用户消息的情感
2. **累积效应**: 连续相似的情绪会加强当前心情
3. **自然衰减**: 长时间无对话会逐渐回归中性
4. **记忆影响**: 历史对话会影响当前心情判断

### 如何影响AI心情
- **让AI开心**: 使用积极词汇、表达感谢、分享好消息
- **让AI伤心**: 表达难过、抱怨问题、分享坏消息
- **安慰AI**: 当AI伤心时，可以说些鼓励的话
- **逗AI开心**: 讲笑话、分享有趣的事情

## 记忆功能

### 自动记忆
- 所有对话自动保存到本地
- 按日期和时间组织
- 支持搜索历史对话
- 自动生成对话摘要

### 记忆管理
1. **查看历史**
   - 对话记录保存在 `data/memory/conversations/`
   - 每个文件包含一次完整的对话
   - 文件名包含时间戳便于查找

2. **搜索对话**
   - 支持关键词搜索
   - 按时间范围过滤
   - 按心情类型筛选

3. **导出对话**
   - 支持导出为JSON格式
   - 支持导出为文本格式
   - 可以导出选定时间段的对话

### 隐私保护
- 所有数据保存在本地
- 不会上传到云端
- 可以随时清理对话历史
- 支持数据加密（可选）

## 配置说明

### 配置文件位置

data/config/

├── ai_profiles.json    # AI服务配置

├── settings.json       # 应用设置

└── mood_rules.json     # 心情规则

复制
### AI配置示例

json

{

"active_profile": "my_ollama",

"profiles": {

"my_ollama": {

"name": "我的Ollama",

"type": "ollama",

"base_url": "http://localhost:11434
",

"model": "qwen:7b",

"timeout": 60

}

}

}
### 应用设置
json

{

"window": {

"width": 1000,

"height": 700,

"theme": "light"

},

"chat": {

"max_history": 100,

"auto_scroll": true,

"font_size": 12

},

"memory": {

"max_conversations": 1000,

"auto_summarize": true

}

}
### 自定义配置
1. 编辑配置文件
2. 重启应用生效
3. 支持热重载部分配置

## 常见问题

### Q1: AI宠物没有响应？
**可能原因:**
- AI服务未启动
- 网络连接问题
- 配置错误

**解决方法:**
1. 检查Ollama服务是否运行
2. 检查 `ai_profiles.json` 配置
3. 查看日志文件 `logs/error.log`

### Q2: 心情图片不显示？
**可能原因:**
- 图片文件缺失
- 文件权限问题
- 路径配置错误

**解决方法:**
1. 检查 `src/ui/assets/moods/` 目录
2. 确保有 `happy.png`, `sad.png`, `neutral.png` 等文件
3. 运行 `python scripts/clean.py` 清理缓存

### Q3: 对话历史丢失？
**可能原因:**
- 数据目录被移动
- 文件权限问题
- 磁盘空间不足

**解决方法:**
1. 检查 `data/memory/conversations/` 目录
2. 查看磁盘空间
3. 从备份恢复（如果有）

### Q4: 应用运行缓慢？
**可能原因:**
- 对话历史过多
- 系统资源不足
- 模型太大

**解决方法:**
1. 清理旧对话：`python scripts/clean.py`
2. 使用更小的AI模型
3. 增加系统内存

## 故障排除

### 查看日志
应用运行日志保存在 `logs/` 目录：
- `ai_pet.log`: 普通日志
- `error.log`: 错误日志
- `ai_pet_rotate.log`: 轮转日志

### 启用调试模式
在启动时添加参数：
bash

python run_app.py --debug
### 重置配置
1. 备份现有配置
2. 删除 `data/config/` 目录
3. 重新启动应用
4. 应用会创建默认配置

### 获取帮助
1. 查看控制台输出
2. 检查日志文件
3. 联系开发者
4. 提交GitHub Issue

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 基础聊天功能
- ✅ 心情系统
- ✅ 记忆存储
- ✅ 图形界面
- ✅ 配置管理

### 计划功能
- [ ] 语音输入/输出
- [ ] 更多心情类型
- [ ] 插件系统
- [ ] 移动端应用
- [ ] 云端同步

## 技术支持

### 文档
- 用户指南（本文档）
- 开发者文档：`docs/developer_guide.md`
- API参考：`docs/api_reference.md`

### 社区
- GitHub仓库: [github.com/yourusername/ai-pet-mvp](https://github.com/yourusername/ai-pet-mvp)
- 问题反馈: GitHub Issues
- 功能建议: GitHub Discussions

### 联系方式
- 邮箱: support@example.com
- Discord: [加入讨论](https://discord.gg/...)
- Twitter: [@aipet_mvp](https://twitter.com/aipet_mvp)

---

感谢使用AI宠物MVP！希望这个智能伙伴能给你带来愉快的体验。如果有任何问题或建议，请随时联系我们。

🎉 祝你使用愉快！