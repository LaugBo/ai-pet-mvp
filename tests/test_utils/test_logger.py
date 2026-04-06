#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统测试
"""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

from src.utils.logger import (
    AIPetLogger, ColorFormatter, get_logger, 
    debug, info, warning, error, critical, exception
)


class TestAIPetLogger:
    """AI宠物日志器测试"""
    
    def test_initialization(self, temp_dir):
        """测试初始化"""
        # 使用临时目录
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_logger", "DEBUG")
            
            assert logger.name == "test_logger"
            assert logger.log_level == "DEBUG"
            assert logger.logger is not None
            assert logger.log_dir is not None
    
    def test_log_levels(self, temp_dir):
        """测试日志级别"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_levels", "DEBUG")
            
            # 测试所有级别
            logger.debug("调试消息")
            logger.info("信息消息")
            logger.warning("警告消息")
            logger.error("错误消息")
            logger.critical("严重错误消息")
            
            # 应该没有异常
    
    def test_log_with_kwargs(self, temp_dir):
        """测试带参数的日志"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_kwargs", "INFO")
            
            logger.info("操作完成", user="test", action="login", duration=1.5)
    
    def test_exception_logging(self, temp_dir):
        """测试异常日志"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_exception", "ERROR")
            
            try:
                raise ValueError("测试异常")
            except Exception as e:
                logger.exception("捕获异常", exc_info=e)
    
    def test_get_log_files(self, temp_dir):
        """测试获取日志文件"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            # 创建一些日志文件
            log_dir = temp_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            (log_dir / "test1.log").write_text("日志内容1")
            (log_dir / "test2.log").write_text("日志内容2")
            
            logger = AIPetLogger("test_files", "INFO")
            logger.log_dir = log_dir
            
            log_files = logger.get_log_files()
            
            assert len(log_files) == 2
            assert "test1.log" in log_files
            assert "test2.log" in log_files
    
    def test_clear_old_logs(self, temp_dir):
        """测试清理旧日志"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_clear", "INFO")
            
            # 模拟日志目录
            log_dir = temp_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            logger.log_dir = log_dir
            
            # 创建一些日志文件
            (log_dir / "old.log").write_text("旧日志")
            (log_dir / "recent.log").write_text("新日志")
            
            # 清理（应该不会删除，因为文件太新）
            logger.clear_old_logs(days=30)
            
            # 两个文件都应该存在
            assert (log_dir / "old.log").exists()
            assert (log_dir / "recent.log").exists()
    
    def test_log_system_info(self, temp_dir):
        """测试记录系统信息"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger = AIPetLogger("test_sysinfo", "INFO")
            
            # 模拟psutil
            with patch('src.utils.logger.psutil') as mock_psutil:
                mock_psutil.virtual_memory.return_value.total = 1024**3  # 1GB
                mock_psutil.virtual_memory.return_value.available = 512 * 1024**2  # 512MB
                mock_psutil.cpu_count.return_value = 4
                mock_psutil.cpu_count.logical = 8
                
                logger.log_system_info()
    
    def test_singleton_pattern(self, temp_dir):
        """测试单例模式"""
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_dir
            
            logger1 = get_logger("singleton_test")
            logger2 = get_logger("singleton_test")
            
            # 应该是同一个实例
            assert logger1 is logger2


class TestColorFormatter:
    """颜色格式化器测试"""
    
    def test_format_with_colors(self):
        """测试带颜色的格式化"""
        formatter = ColorFormatter('%(levelname)s %(message)s')
        
        # 创建日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="测试消息",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # 应该包含颜色代码
        assert "\x1b[" in formatted  # ANSI颜色代码


class TestShortcutFunctions:
    """快捷函数测试"""
    
    def test_debug_function(self, temp_dir):
        """测试debug快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            debug("调试消息", extra="data")
            
            mock_logger.debug.assert_called_with("调试消息", extra="data")
    
    def test_info_function(self, temp_dir):
        """测试info快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            info("信息消息", user="test")
            
            mock_logger.info.assert_called_with("信息消息", user="test")
    
    def test_warning_function(self, temp_dir):
        """测试warning快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            warning("警告消息", code=1001)
            
            mock_logger.warning.assert_called_with("警告消息", code=1001)
    
    def test_error_function(self, temp_dir):
        """测试error快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            error("错误消息", error_type="test")
            
            mock_logger.error.assert_called_with("错误消息", error_type="test")
    
    def test_critical_function(self, temp_dir):
        """测试critical快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            critical("严重错误", fatal=True)
            
            mock_logger.critical.assert_called_with("严重错误", fatal=True)
    
    def test_exception_function(self, temp_dir):
        """测试exception快捷函数"""
        with patch('src.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            test_exception = ValueError("测试异常")
            
            exception("异常消息", exc_info=test_exception, extra="data")
            
            mock_logger.exception.assert_called_with(
                "异常消息", exc_info=test_exception, extra="data"
            )


class TestLoggerIntegration:
    """日志器集成测试"""
    
    def test_logger_with_real_files(self, temp_dir):
        """测试真实的文件日志"""
        # 创建临时项目目录结构
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        
        with patch('src.utils.logger.Path') as mock_path:
            # 模拟项目根目录
            mock_path.return_value.parent.parent.parent = project_dir
            
            # 创建日志器
            logger = AIPetLogger("file_test", "DEBUG")
            
            # 记录一些日志
            logger.debug("文件调试")
            logger.info("文件信息")
            logger.warning("文件警告")
            
            # 检查日志文件是否创建
            log_files = list(logger.log_dir.glob("*.log"))
            assert len(log_files) > 0
            
            # 检查文件内容
            for log_file in log_files:
                if log_file.name.endswith("_ai_pet.log"):
                    content = log_file.read_text(encoding='utf-8')
                    assert "文件调试" in content
                    assert "文件信息" in content
                    assert "文件警告" in content
    
    def test_log_rotation(self, temp_dir):
        """测试日志轮转"""
        project_dir = temp_dir / "rotation_project"
        project_dir.mkdir()
        
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = project_dir
            
            logger = AIPetLogger("rotation_test", "INFO")
            
            # 写入大量日志（触发轮转）
            for i in range(1000):
                logger.info(f"测试日志 {i}" * 10)  # 长消息
            
            # 检查轮转文件
            rotate_files = list(logger.log_dir.glob("*rotate*"))
            assert len(rotate_files) > 0
    
    def test_multiple_loggers(self, temp_dir):
        """测试多个日志器"""
        project_dir = temp_dir / "multi_project"
        project_dir.mkdir()
        
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = project_dir
            
            # 创建不同名称的日志器
            logger1 = AIPetLogger("module1", "INFO")
            logger2 = AIPetLogger("module2", "DEBUG")
            
            logger1.info("来自模块1")
            logger2.debug("来自模块2")
            
            # 应该创建不同的日志文件
            log_files = list(project_dir.glob("logs/*.log"))
            assert len(log_files) > 0
    
    def test_log_level_filtering(self, temp_dir):
        """测试日志级别过滤"""
        project_dir = temp_dir / "level_project"
        project_dir.mkdir()
        
        with patch('src.utils.logger.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = project_dir
            
            # 设置为WARNING级别
            logger = AIPetLogger("level_test", "WARNING")
            
            # 这些应该被过滤掉
            logger.debug("调试消息 - 不应该出现")
            logger.info("信息消息 - 不应该出现")
            
            # 这些应该出现
            logger.warning("警告消息 - 应该出现")
            logger.error("错误消息 - 应该出现")
            
            # 检查控制台输出
            # 注意：实际测试中难以检查控制台输出，这里主要是确保不崩溃