#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理脚本
用于清理AI宠物项目的临时文件和缓存
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.helpers import time_it, safe_execute, format_size
from src.utils.error_handler import safe_call, ErrorHandler


class CleanManager:
    """清理管理器"""
    
    def __init__(self):
        """初始化清理管理器"""
        self.project_root = Path(__file__).parent.parent
        self.logger = get_logger("clean")
        self.error_handler = ErrorHandler(self.logger)
        
        # 定义清理规则
        self.clean_rules = [
            {
                "name": "Python缓存",
                "patterns": ["__pycache__", "*.pyc", "*.pyo", "*.pyd"],
                "paths": [self.project_root],
                "description": "Python编译缓存文件",
                "recursive": True
            },
            {
                "name": "临时文件",
                "patterns": ["*.tmp", "*.temp", "*.bak", "*.swp", "~*"],
                "paths": [self.project_root],
                "description": "临时文件",
                "recursive": True
            },
            {
                "name": "IDE配置",
                "patterns": [".vscode", ".idea", ".vs", "*.code-workspace"],
                "paths": [self.project_root],
                "description": "IDE配置文件",
                "recursive": False
            },
            {
                "name": "版本控制",
                "patterns": [".git", ".svn", ".hg"],
                "paths": [self.project_root],
                "description": "版本控制目录",
                "recursive": False
            },
            {
                "name": "Python虚拟环境",
                "patterns": ["venv", ".venv", "env", ".env", "virtualenv"],
                "paths": [self.project_root],
                "description": "Python虚拟环境",
                "recursive": False
            },
            {
                "name": "构建产物",
                "patterns": ["build", "dist", "*.egg-info", "__pycache__"],
                "paths": [self.project_root],
                "description": "Python构建产物",
                "recursive": True
            },
            {
                "name": "日志文件",
                "patterns": ["*.log", "logs/*.log"],
                "paths": [self.project_root],
                "description": "日志文件",
                "recursive": True,
                "age_days": 7  # 只清理7天前的日志
            }
        ]
        
        # 排除的路径（绝对不清理）
        self.exclude_paths = [
            self.project_root / "data",
            self.project_root / "src",
            self.project_root / "requirements.txt",
            self.project_root / "run_app.py",
            self.project_root / "README.md"
        ]
    
    def _should_exclude(self, path: Path) -> bool:
        """检查路径是否应该排除"""
        # 检查是否在排除列表中
        for exclude_path in self.exclude_paths:
            try:
                if path.is_relative_to(exclude_path):
                    return True
            except:
                pass
        
        # 检查是否是重要文件
        important_files = [
            "__init__.py",
            "ai_profiles.json",
            "settings.json",
            "mood_rules.json"
        ]
        
        if path.name in important_files:
            return True
        
        return False
    
    @safe_call(operation="扫描可清理文件")
    def scan(self, dry_run: bool = True) -> Dict[str, List[Path]]:
        """
        扫描可清理的文件
        
        Args:
            dry_run: 是否模拟运行（不实际删除）
        
        Returns:
            按类型分类的文件列表
        """
        self.logger.info(f"开始扫描可清理文件 (dry_run={dry_run})")
        
        found_files = {}
        total_size = 0
        
        for rule in self.clean_rules:
            rule_name = rule["name"]
            found_files[rule_name] = []
            
            for base_path in rule["paths"]:
                base_path = Path(base_path)
                if not base_path.exists():
                    continue
                
                # 根据是否递归扫描
                if rule.get("recursive", True):
                    paths = base_path.rglob("*")
                else:
                    paths = base_path.glob("*")
                
                for path in paths:
                    # 检查是否匹配模式
                    if self._matches_pattern(path, rule["patterns"]):
                        # 检查是否应该排除
                        if self._should_exclude(path):
                            continue
                        
                        # 检查文件年龄
                        if rule.get("age_days"):
                            try:
                                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                                age = datetime.now() - mtime
                                if age.days < rule["age_days"]:
                                    continue
                            except:
                                pass
                        
                        found_files[rule_name].append(path)
            
            # 计算大小
            rule_size = sum(f.stat().st_size for f in found_files[rule_name] if f.is_file())
            total_size += rule_size
            
            if found_files[rule_name]:
                self.logger.info(f"  {rule_name}: 找到 {len(found_files[rule_name])} 个文件，"
                               f"大小: {format_size(rule_size)}")
        
        self.logger.info(f"扫描完成，总共找到 {sum(len(files) for files in found_files.values())} 个文件，"
                       f"总大小: {format_size(total_size)}")
        
        return found_files
    
    def _matches_pattern(self, path: Path, patterns: List[str]) -> bool:
        """检查路径是否匹配模式"""
        import fnmatch
        
        for pattern in patterns:
            # 处理目录模式
            if pattern.endswith('/') or pattern.endswith('\\'):
                pattern = pattern.rstrip('/\\')
                if path.is_dir() and fnmatch.fnmatch(path.name, pattern):
                    return True
            
            # 处理文件模式
            elif fnmatch.fnmatch(path.name, pattern):
                return True
            
            # 处理相对路径模式
            elif '/' in pattern or '\\' in pattern:
                try:
                    if path.match(pattern):
                        return True
                except:
                    pass
        
        return False
    
    @safe_call(operation="清理文件")
    def clean(self, rule_names: List[str] = None, dry_run: bool = False) -> Dict[str, Dict]:
        """
        清理文件
        
        Args:
            rule_names: 要清理的规则名称列表，为None时清理所有
            dry_run: 是否模拟运行
        
        Returns:
            清理结果统计
        """
        # 扫描文件
        found_files = self.scan(dry_run=True)
        
        if rule_names:
            # 只清理指定的规则
            files_to_clean = {name: found_files.get(name, []) for name in rule_names}
        else:
            # 清理所有规则
            files_to_clean = found_files
        
        results = {}
        total_deleted = 0
        total_freed = 0
        
        self.logger.info(f"开始清理文件 (dry_run={dry_run})")
        
        for rule_name, files in files_to_clean.items():
            if not files:
                continue
            
            rule_results = {
                "total": len(files),
                "deleted": 0,
                "failed": 0,
                "freed": 0,
                "errors": []
            }
            
            self.logger.info(f"清理 {rule_name}: {len(files)} 个文件")
            
            for file_path in files:
                try:
                    # 计算文件大小
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                    elif file_path.is_dir():
                        file_size = self._get_dir_size(file_path)
                    else:
                        file_size = 0
                    
                    if not dry_run:
                        # 实际删除
                        if file_path.is_file():
                            file_path.unlink()
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                        
                        rule_results["deleted"] += 1
                        rule_results["freed"] += file_size
                        self.logger.debug(f"  已删除: {file_path}")
                    else:
                        # 模拟运行
                        rule_results["deleted"] += 1
                        rule_results["freed"] += file_size
                        self.logger.debug(f"  [模拟] 将删除: {file_path}")
                        
                except Exception as e:
                    rule_results["failed"] += 1
                    rule_results["errors"].append(str(e))
                    self.logger.error(f"  删除失败: {file_path}", error=str(e))
            
            total_deleted += rule_results["deleted"]
            total_freed += rule_results["freed"]
            results[rule_name] = rule_results
            
            if rule_results["deleted"] > 0:
                self.logger.info(f"  {rule_name}: 删除 {rule_results['deleted']} 个文件，"
                               f"释放 {format_size(rule_results['freed'])}")
        
        self.logger.info(f"清理完成: 总共删除 {total_deleted} 个文件，"
                       f"释放 {format_size(total_freed)}")
        
        return results
    
    def _get_dir_size(self, directory: Path) -> int:
        """获取目录大小"""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
        return total_size
    
    @safe_call(operation="清理旧日志")
    def clean_old_logs(self, days: int = 7, dry_run: bool = False) -> Dict[str, int]:
        """
        清理旧日志文件
        
        Args:
            days: 保留天数
            dry_run: 是否模拟运行
        
        Returns:
            清理统计
        """
        log_dir = self.project_root / "logs"
        if not log_dir.exists():
            self.logger.warning("日志目录不存在")
            return {"deleted": 0, "failed": 0, "freed": 0}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted = 0
        failed = 0
        freed = 0
        
        self.logger.info(f"清理 {days} 天前的日志文件 (dry_run={dry_run})")
        
        for log_file in log_dir.glob("*.log"):
            try:
                # 检查文件修改时间
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    file_size = log_file.stat().st_size
                    
                    if not dry_run:
                        log_file.unlink()
                        self.logger.info(f"  删除旧日志: {log_file.name}")
                    else:
                        self.logger.info(f"  [模拟] 将删除旧日志: {log_file.name}")
                    
                    deleted += 1
                    freed += file_size
                    
            except Exception as e:
                failed += 1
                self.logger.error(f"  删除日志失败: {log_file}", error=str(e))
        
        self.logger.info(f"日志清理完成: 删除 {deleted} 个文件，释放 {format_size(freed)}")
        
        return {
            "deleted": deleted,
            "failed": failed,
            "freed": freed
        }
    
    @safe_call(operation="清理内存数据")
    def clean_memory_data(self, 
                         keep_days: int = 30,
                         keep_count: int = 100,
                         dry_run: bool = False) -> Dict[str, int]:
        """
        清理旧的内存数据
        
        Args:
            keep_days: 保留天数
            keep_count: 每个目录保留的文件数量
            dry_run: 是否模拟运行
        
        Returns:
            清理统计
        """
        memory_dir = self.project_root / "data" / "memory"
        if not memory_dir.exists():
            self.logger.warning("内存目录不存在")
            return {"deleted": 0, "failed": 0, "freed": 0}
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        deleted = 0
        failed = 0
        freed = 0
        
        self.logger.info(f"清理内存数据 (保留{keep_days}天，每个目录最多{keep_count}个文件)")
        
        # 清理对话记录
        conversations_dir = memory_dir / "conversations"
        if conversations_dir.exists():
            conv_stats = self._clean_directory_by_age(
                conversations_dir, cutoff_date, keep_count, dry_run, "*.json")
            deleted += conv_stats["deleted"]
            failed += conv_stats["failed"]
            freed += conv_stats["freed"]
        
        # 清理心情记录
        moods_dir = memory_dir / "moods"
        if moods_dir.exists():
            mood_stats = self._clean_directory_by_age(
                moods_dir, cutoff_date, keep_count, dry_run, "*.json")
            deleted += mood_stats["deleted"]
            failed += mood_stats["failed"]
            freed += mood_stats["freed"]
        
        # 清理摘要
        summaries_dir = memory_dir / "summaries"
        if summaries_dir.exists():
            sum_stats = self._clean_directory_by_age(
                summaries_dir, cutoff_date, keep_count, dry_run, "*.json")
            deleted += sum_stats["deleted"]
            failed += sum_stats["failed"]
            freed += sum_stats["freed"]
        
        self.logger.info(f"内存数据清理完成: 删除 {deleted} 个文件，释放 {format_size(freed)}")
        
        return {
            "deleted": deleted,
            "failed": failed,
            "freed": freed
        }
    
    def _clean_directory_by_age(self, 
                               directory: Path,
                               cutoff_date: datetime,
                               keep_count: int,
                               dry_run: bool,
                               pattern: str = "*") -> Dict[str, int]:
        """按时间清理目录中的文件"""
        deleted = 0
        failed = 0
        freed = 0
        
        # 获取所有文件并按修改时间排序
        files = []
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    files.append((file_path, mtime, file_path.stat().st_size))
                except:
                    pass
        
        # 按时间排序（从旧到新）
        files.sort(key=lambda x: x[1])
        
        # 计算要删除的文件
        files_to_delete = []
        for i, (file_path, mtime, size) in enumerate(files):
            if mtime < cutoff_date or i < len(files) - keep_count:
                files_to_delete.append((file_path, size))
        
        # 删除文件
        for file_path, size in files_to_delete:
            try:
                if not dry_run:
                    file_path.unlink()
                    self.logger.debug(f"  删除: {file_path.relative_to(self.project