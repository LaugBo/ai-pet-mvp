#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统模块
为AI宠物MVP项目提供统一的日志记录功能
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class AIPetLogger:
    """AI宠物日志管理器"""
    
    # 日志级别颜色映射
    LEVEL_COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    # 日志级别符号
    LEVEL_SYMBOLS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    
    def __init__(self, name: str = "ai_pet", log_level: str = "INFO"):
        """
        初始化日志管理器
        
        Args:
            name: 日志器名称
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_level = log_level
        self.logger = None
        self.log_dir = None
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        # 创建日志目录
        project_root = Path(__file__).parent.parent.parent
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志器
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 控制台处理器（带颜色）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level.upper()))
        console_formatter = ColorFormatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器 - 普通日志
        log_file = self.log_dir / f"{datetime.now().strftime('%Y%m')}_ai_pet.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 文件处理器 - 错误日志
        error_file = self.log_dir / f"{datetime.now().strftime('%Y%m')}_error.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # 文件处理器 - 按大小轮转
        rotate_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "ai_pet_rotate.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        rotate_handler.setLevel(logging.INFO)
        rotate_handler.setFormatter(file_formatter)
        self.logger.addHandler(rotate_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs) -> None:
        """严重错误日志"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def exception(self, message: str, exc_info: Optional[Exception] = None, **kwargs) -> None:
        """异常日志"""
        if exc_info:
            self.logger.exception(self._format_message(message, **kwargs), exc_info=exc_info)
        else:
            self.logger.exception(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """格式化日志消息"""
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {extra_info}"
        return message
    
    def get_log_files(self) -> Dict[str, Path]:
        """获取所有日志文件"""
        log_files = {}
        for file in self.log_dir.glob("*.log"):
            if file.is_file():
                log_files[file.name] = file
        return log_files
    
    def clear_old_logs(self, days: int = 30) -> None:
        """清理指定天数前的旧日志"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        for log_file in self.log_dir.glob("*.log"):
            if log_file.is_file():
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    try:
                        log_file.unlink()
                        deleted_count += 1
                        self.info(f"删除旧日志文件: {log_file.name}")
                    except Exception as e:
                        self.error(f"删除日志文件失败: {log_file.name}", error=str(e))
        
        if deleted_count > 0:
            self.info(f"清理完成，共删除 {deleted_count} 个旧日志文件")
    
    def log_system_info(self) -> None:
        """记录系统信息"""
        import platform
        import psutil
        
        system_info = {
            "系统": platform.system(),
            "版本": platform.version(),
            "处理器": platform.processor(),
            "Python版本": platform.python_version(),
            "内存总量(GB)": round(psutil.virtual_memory().total / (1024**3), 2),
            "内存可用(GB)": round(psutil.virtual_memory().available / (1024**3), 2),
            "CPU核心数": psutil.cpu_count(logical=False),
            "逻辑CPU数": psutil.cpu_count(logical=True)
        }
        
        self.info("系统信息", **system_info)
    
    def get_logger(self) -> logging.Logger:
        """获取原生logging.Logger对象"""
        return self.logger


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in AIPetLogger.LEVEL_COLORS:
            color = AIPetLogger.LEVEL_COLORS[levelname]
            symbol = AIPetLogger.LEVEL_SYMBOLS.get(levelname, '')
            record.levelname = f"{color}{symbol} {levelname:8s}{Style.RESET_ALL}"
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        
        return super().format(record)


# 全局日志实例
_logger_instance = None


def get_logger(name: str = "ai_pet", log_level: str = "INFO") -> AIPetLogger:
    """获取日志器实例（单例模式）"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AIPetLogger(name, log_level)
    return _logger_instance


def setup_logging(name: str = "ai_pet", log_level: str = "INFO") -> AIPetLogger:
    """设置日志并返回日志器"""
    return get_logger(name, log_level)


# 快捷函数
def debug(msg: str, **kwargs):
    get_logger().debug(msg, **kwargs)

def info(msg: str, **kwargs):
    get_logger().info(msg, **kwargs)

def warning(msg: str, **kwargs):
    get_logger().warning(msg, **kwargs)

def error(msg: str, **kwargs):
    get_logger().error(msg, **kwargs)

def critical(msg: str, **kwargs):
    get_logger().critical(msg, **kwargs)

def exception(msg: str, exc_info: Optional[Exception] = None, **kwargs):
    get_logger().exception(msg, exc_info=exc_info, **kwargs)