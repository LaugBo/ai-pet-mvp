#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助工具模块
提供各种通用工具函数
"""

import os
import sys
import json
import time
import random
import string
import hashlib
import threading
import functools
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
import inspect
import traceback


class Singleton(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def time_it(func: Callable) -> Callable:
    """计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 获取函数名
        func_name = func.__name__
        module_name = func.__module__
        
        # 格式化时间
        if elapsed < 0.001:
            time_str = f"{elapsed*1e6:.2f}μs"
        elif elapsed < 1:
            time_str = f"{elapsed*1000:.2f}ms"
        else:
            time_str = f"{elapsed:.2f}s"
        
        print(f"⏱️  [{module_name}.{func_name}] 执行时间: {time_str}")
        return result
    return wrapper


def retry(max_retries: int = 3, delay: float = 1.0, 
          exceptions: Tuple = (Exception,), logger=None):
    """重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0 and logger:
                        logger.info(f"重试 {func.__name__} 第{attempt}次...")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        if logger:
                            logger.error(f"{func.__name__} 重试{max_retries}次后失败: {str(e)}")
                        raise
            raise last_exception
        return wrapper
    return decorator


def safe_execute(func: Callable, default_return: Any = None, logger=None) -> Any:
    """
    安全执行函数，捕获所有异常
    
    Args:
        func: 要执行的函数
        default_return: 异常时的默认返回值
        logger: 日志器
    
    Returns:
        函数结果或默认值
    """
    try:
        return func()
    except Exception as e:
        if logger:
            logger.error(f"安全执行失败: {func.__name__ if hasattr(func, '__name__') else '匿名函数'}", 
                        error=str(e))
        return default_return


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:.0f}h {minutes:.0f}m {secs:.0f}s"


def generate_id(length: int = 8, prefix: str = "") -> str:
    """生成随机ID"""
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_str}" if prefix else random_str


def md5_hash(data: Union[str, bytes]) -> str:
    """计算MD5哈希"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()


def json_pretty(data: Any, indent: int = 2) -> str:
    """美化JSON输出"""
    return json.dumps(data, ensure_ascii=False, indent=indent)


def get_file_info(filepath: Union[str, Path]) -> Dict[str, Any]:
    """获取文件信息"""
    path = Path(filepath)
    if not path.exists():
        return {}
    
    stat = path.stat()
    return {
        "filename": path.name,
        "path": str(path.absolute()),
        "size": stat.st_size,
        "size_formatted": format_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "type": "file" if path.is_file() else "directory"
    }


def find_files(directory: Union[str, Path], pattern: str = "**/*", 
               recursive: bool = True) -> List[Path]:
    """查找文件"""
    dir_path = Path(directory)
    if not recursive:
        pattern = pattern.replace("**/", "")
    
    files = list(dir_path.glob(pattern))
    return [f for f in files if f.is_file()]


def read_lines(filepath: Union[str, Path], encoding: str = "utf-8") -> List[str]:
    """读取文件所有行"""
    with open(filepath, 'r', encoding=encoding) as f:
        return [line.rstrip('\n') for line in f.readlines()]


def write_lines(filepath: Union[str, Path], lines: List[str], encoding: str = "utf-8") -> None:
    """写入文件行"""
    with open(filepath, 'w', encoding=encoding) as f:
        f.write('\n'.join(lines))


def deep_update(original: Dict, update: Dict) -> Dict:
    """深度更新字典"""
    for key, value in update.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            deep_update(original[key], value)
        else:
            original[key] = value
    return original


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten(nested_list: List) -> List:
    """展平嵌套列表"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def get_caller_info(levels: int = 2) -> Dict[str, str]:
    """获取调用者信息"""
    frame = inspect.currentframe()
    for _ in range(levels):
        frame = frame.f_back if frame else None
    
    if frame:
        info = inspect.getframeinfo(frame)
        return {
            "filename": info.filename,
            "function": info.function,
            "lineno": info.lineno
        }
    return {}


def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """在新线程中运行函数"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


def run_in_background(func: Callable, delay: float = 0, *args, **kwargs) -> threading.Timer:
    """在后台延迟运行函数"""
    def wrapper():
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"后台任务失败: {e}")
    
    timer = threading.Timer(delay, wrapper)
    timer.daemon = True
    timer.start()
    return timer


class Timer:
    """计时器类"""
    
    def __init__(self, name: str = "计时器"):
        self.name = name
        self.start_time = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
        print(f"⏱️  {self.name}: {self.format_result()}")
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """停止计时"""
        if self.start_time:
            self.elapsed = time.time() - self.start_time
            self.start_time = None
    
    def format_result(self) -> str:
        """格式化结果"""
        return format_time(self.elapsed)
    
    def get_elapsed(self) -> float:
        """获取经过的时间"""
        if self.start_time:
            return time.time() - self.start_time
        return self.elapsed


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        """等待直到可以调用"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
    
    def __call__(self, func):
        """装饰器形式"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


def validate_email(email: str) -> bool:
    """简单邮箱验证"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """简单URL验证"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import psutil
    
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "memory_total": format_size(psutil.virtual_memory().total),
        "memory_available": format_size(psutil.virtual_memory().available),
        "memory_used_percent": f"{psutil.virtual_memory().percent}%",
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_percent": f"{psutil.cpu_percent(interval=1)}%",
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }


def print_system_info():
    """打印系统信息"""
    info = get_system_info()
    print("\n" + "="*50)
    print("系统信息")
    print("="*50)
    for key, value in info.items():
        print(f"{key:20}: {value}")
    print("="*50)