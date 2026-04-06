#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份脚本
用于备份AI宠物项目的数据和配置
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.helpers import time_it, safe_execute, format_size
from src.utils.error_handler import safe_call, ErrorHandler


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        初始化备份管理器
        
        Args:
            backup_dir: 备份目录，默认在项目根目录下的backups文件夹
        """
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = backup_dir or (self.project_root / "backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self.logger = get_logger("backup")
        self.error_handler = ErrorHandler(self.logger)
        
        # 要备份的目录和文件
        self.backup_items = [
            {
                "name": "config",
                "path": self.project_root / "data" / "config",
                "type": "directory",
                "description": "配置文件"
            },
            {
                "name": "memory",
                "path": self.project_root / "data" / "memory",
                "type": "directory",
                "description": "记忆数据"
            },
            {
                "name": "logs",
                "path": self.project_root / "logs",
                "type": "directory",
                "description": "日志文件",
                "optional": True
            }
        ]
        
        # 要排除的文件模式
        self.exclude_patterns = [
            "*.tmp",
            "*.temp",
            "*.log",  # 日志文件单独处理
            "*.bak",
            "__pycache__",
            ".git",
            ".vscode",
            ".idea"
        ]
    
    @safe_call(operation="创建备份")
    def create_backup(self, 
                     backup_name: Optional[str] = None,
                     compress: bool = True,
                     include_logs: bool = False) -> Path:
        """
        创建备份
        
        Args:
            backup_name: 备份名称，默认为时间戳
            compress: 是否压缩为zip
            include_logs: 是否包含日志文件
        
        Returns:
            备份文件路径
        """
        # 生成备份名称
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ai_pet_backup_{timestamp}"
        
        self.logger.info(f"开始创建备份: {backup_name}")
        
        # 临时备份目录
        temp_backup_dir = self.backup_dir / "temp" / backup_name
        temp_backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 备份每个项目
            total_size = 0
            backup_info = {
                "name": backup_name,
                "created_at": datetime.now().isoformat(),
                "items": [],
                "total_size": 0
            }
            
            for item in self.backup_items:
                # 检查是否包含日志
                if item["name"] == "logs" and not include_logs:
                    continue
                
                # 检查路径是否存在
                if not item["path"].exists():
                    if item.get("optional", False):
                        self.logger.warning(f"跳过不存在的可选项目: {item['name']}")
                        continue
                    else:
                        raise FileNotFoundError(f"备份项目不存在: {item['path']}")
                
                # 执行备份
                item_size = self._backup_item(item, temp_backup_dir)
                total_size += item_size
                
                backup_info["items"].append({
                    "name": item["name"],
                    "type": item["type"],
                    "path": str(item["path"]),
                    "size": item_size,
                    "size_formatted": format_size(item_size)
                })
            
            # 创建备份信息文件
            backup_info["total_size"] = total_size
            backup_info["total_size_formatted"] = format_size(total_size)
            
            info_file = temp_backup_dir / "backup_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"备份信息已保存: {info_file}")
            
            # 如果压缩，创建zip文件
            if compress:
                backup_path = self._create_zip_backup(temp_backup_dir, backup_name)
                # 清理临时目录
                shutil.rmtree(temp_backup_dir)
            else:
                backup_path = temp_backup_dir
                # 移动到正式备份目录
                final_path = self.backup_dir / backup_name
                if final_path.exists():
                    shutil.rmtree(final_path)
                shutil.move(temp_backup_dir, final_path)
                backup_path = final_path
            
            self.logger.info(f"备份创建完成: {backup_path}")
            self.logger.info(f"总大小: {format_size(total_size)}")
            
            # 保存备份记录
            self._save_backup_record(backup_info, str(backup_path))
            
            return backup_path
            
        except Exception as e:
            # 清理临时目录
            if temp_backup_dir.exists():
                shutil.rmtree(temp_backup_dir, ignore_errors=True)
            raise
    
    def _backup_item(self, item: Dict[str, Any], target_dir: Path) -> int:
        """备份单个项目"""
        item_type = item["type"]
        source_path = item["path"]
        target_path = target_dir / item["name"]
        
        self.logger.info(f"备份{item['description']}: {source_path}")
        
        if item_type == "directory":
            return self._backup_directory(source_path, target_path)
        elif item_type == "file":
            return self._backup_file(source_path, target_path)
        else:
            raise ValueError(f"不支持的备份类型: {item_type}")
    
    def _backup_directory(self, source_dir: Path, target_dir: Path) -> int:
        """备份目录"""
        total_size = 0
        
        # 复制目录结构
        for root, dirs, files in os.walk(source_dir):
            # 跳过排除的目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            # 创建目标目录
            rel_path = Path(root).relative_to(source_dir)
            target_root = target_dir / rel_path
            target_root.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            for file in files:
                if self._should_exclude(file):
                    continue
                
                source_file = Path(root) / file
                target_file = target_root / file
                
                file_size = self._backup_file(source_file, target_file)
                total_size += file_size
        
        return total_size
    
    def _backup_file(self, source_file: Path, target_file: Path) -> int:
        """备份单个文件"""
        try:
            # 获取文件大小
            file_size = source_file.stat().st_size
            
            # 复制文件
            shutil.copy2(source_file, target_file)
            
            return file_size
        except Exception as e:
            self.logger.error(f"备份文件失败: {source_file}", error=str(e))
            return 0
    
    def _should_exclude(self, name: str) -> bool:
        """检查是否应该排除"""
        import fnmatch
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _create_zip_backup(self, source_dir: Path, backup_name: str) -> Path:
        """创建zip备份"""
        zip_path = self.backup_dir / f"{backup_name}.zip"
        
        self.logger.info(f"创建压缩备份: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # 跳过排除的目录
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]
                
                for file in files:
                    if self._should_exclude(file):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def _save_backup_record(self, backup_info: Dict[str, Any], backup_path: str) -> None:
        """保存备份记录"""
        records_file = self.backup_dir / "backup_records.json"
        
        records = []
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        
        # 添加新记录
        record = {
            "name": backup_info["name"],
            "path": backup_path,
            "created_at": backup_info["created_at"],
            "total_size": backup_info["total_size"],
            "total_size_formatted": backup_info["total_size_formatted"],
            "items": len(backup_info["items"])
        }
        records.append(record)
        
        # 只保留最近的20个记录
        if len(records) > 20:
            records = records[-20:]
        
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    @safe_call(operation="列出备份")
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        
        # 检查zip备份
        for zip_file in self.backup_dir.glob("*.zip"):
            backup_info = self._get_backup_info(zip_file)
            if backup_info:
                backups.append(backup_info)
        
        # 检查目录备份
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name != "temp":
                if (backup_dir / "backup_info.json").exists():
                    backup_info = self._get_backup_info(backup_dir)
                    if backup_info:
                        backups.append(backup_info)
        
        # 按创建时间排序
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    def _get_backup_info(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """获取备份信息"""
        try:
            if backup_path.is_file() and backup_path.suffix == ".zip":
                # zip文件
                info = {
                    "name": backup_path.stem,
                    "path": str(backup_path),
                    "type": "zip",
                    "size": backup_path.stat().st_size,
                    "size_formatted": format_size(backup_path.stat().st_size),
                    "created_at": datetime.fromtimestamp(backup_path.stat().st_ctime).isoformat()
                }
                
                # 尝试从zip中读取备份信息
                try:
                    with zipfile.ZipFile(backup_path, 'r') as zipf:
                        if "backup_info.json" in zipf.namelist():
                            with zipf.open("backup_info.json") as f:
                                backup_info = json.load(f)
                                info.update(backup_info)
                except:
                    pass
                
                return info
                
            elif backup_path.is_dir():
                # 目录备份
                info_file = backup_path / "backup_info.json"
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    info["path"] = str(backup_path)
                    info["type"] = "directory"
                    return info
        
        except Exception as e:
            self.logger.error(f"获取备份信息失败: {backup_path}", error=str(e))
        
        return None
    
    @safe_call(operation="恢复备份")
    def restore_backup(self, 
                      backup_name: str,
                      target_dir: Optional[Path] = None,
                      overwrite: bool = False) -> bool:
        """
        恢复备份
        
        Args:
            backup_name: 备份名称
            target_dir: 目标目录，默认为项目根目录
            overwrite: 是否覆盖现有文件
        
        Returns:
            是否恢复成功
        """
        target_dir = target_dir or self.project_root
        backup_path = self._find_backup(backup_name)
        
        if not backup_path:
            self.logger.error(f"备份未找到: {backup_name}")
            return False
        
        self.logger.info(f"开始恢复备份: {backup_name}")
        
        try:
            if backup_path.is_file() and backup_path.suffix == ".zip":
                # 从zip恢复
                return self._restore_from_zip(backup_path, target_dir, overwrite)
            elif backup_path.is_dir():
                # 从目录恢复
                return self._restore_from_directory(backup_path, target_dir, overwrite)
            else:
                raise ValueError(f"不支持的备份格式: {backup_path}")
                
        except Exception as e:
            self.logger.error(f"恢复备份失败: {backup_name}", error=str(e))
            return False
    
    def _find_backup(self, backup_name: str) -> Optional[Path]:
        """查找备份"""
        # 检查zip文件
        zip_path = self.backup_dir / f"{backup_name}.zip"
        if zip_path.exists():
            return zip_path
        
        # 检查目录
        dir_path = self.backup_dir / backup_name
        if dir_path.exists() and dir_path.is_dir():
            return dir_path
        
        # 通过名称查找
        for backup in self.list_backups():
            if backup["name"] == backup_name:
                return Path(backup["path"])
        
        return None
    
    def _restore_from_zip(self, zip_path: Path, target_dir: Path, overwrite: bool) -> bool:
        """从zip文件恢复"""
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # 检查是否覆盖
            if not overwrite:
                for file_info in zipf.infolist():
                    target_file = target_dir / file_info.filename
                    if target_file.exists():
                        self.logger.error(f"文件已存在: {target_file}")
                        return False
            
            # 解压文件
            zipf.extractall(target_dir)
        
        self.logger.info(f"备份恢复完成: {zip_path.name}")
        return True
    
    def _restore_from_directory(self, backup_dir: Path, target_dir: Path, overwrite: bool) -> bool:
        """从目录恢复"""
        # 读取备份信息
        info_file = backup_dir / "backup_info.json"
        if not info_file.exists():
            self.logger.error(f"备份信息文件不存在: {info_file}")
            return False
        
        with open(info_file, 'r', encoding='utf-8') as f:
            backup_info = json.load(f)
        
        # 恢复每个项目
        for item in backup_info.get("items", []):
            source_path = backup_dir / item["name"]
            target_path = target_dir / Path(item["path"]).relative_to(self.project_root)
            
            if not source_path.exists():
                self.logger.warning(f"备份项目不存在: {source_path}")
                continue
            
            if target_path.exists() and not overwrite:
                self.logger.error(f"目标已存在: {target_path}")
                return False
            
            # 复制文件或目录
            if source_path.is_dir():
                shutil.copytree(source_path, target_path, dirs_exist_ok=overwrite)
            else:
                shutil.copy2(source_path, target_path)
            
            self.logger.info(f"恢复: {item['name']} -> {target_path}")
        
        self.logger.info(f"备份恢复完成: {backup_dir.name}")
        return True
    
    @safe_call(operation="清理旧备份")
    def cleanup_old_backups(self, keep_count: int = 5, keep_days: int = 30) -> int:
        """
        清理旧备份
        
        Args:
            keep_count: 保留最新的几个备份
            keep_days: 保留多少天内的备份
        
        Returns:
            删除的备份数量
        """
        backups = self.list_backups()
        if len(backups) <= keep_count:
            self.logger.info(f"备份数量({len(backups)})未超过保留数量({keep_count})，无需清理")
            return 0
        
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        deleted_count = 0
        backups_to_keep = backups[:keep_count]
        
        for backup in backups[keep_count:]:
            backup_path = Path(backup["path"])
            
            # 检查是否在保留天数内
            try:
                created_at = datetime.fromisoformat(backup.get("created_at", ""))
                if created_at > cutoff_date:
                    self.logger.info(f"跳过在保留期内的备份: {backup['name']}")
                    continue
            except:
                pass
            
            # 删除备份
            try:
                if backup_path.is_file():
                    backup_path.unlink()
                elif backup_path.is_dir():
                    shutil.rmtree(backup_path)
                
                deleted_count += 1
                self.logger.info(f"删除旧备份: {backup['name']}")
            except Exception as e:
                self.logger.error(f"删除备份失败: {backup_path}", error=str(e))
        
        # 更新备份记录
        self._update_backup_records(backups_to_keep)
        
        self.logger.info(f"清理完成，共删除 {deleted_count} 个备份")
        return deleted_count
    
    def _update_backup_records(self, remaining_backups: List[Dict[str, Any]]) -> None:
        """更新备份记录"""
        records_file = self.backup_dir / "backup_records.json"
        
        # 只保留剩余的备份记录
        remaining_names = {b["name"] for b in remaining_backups}
        records = []
        
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                all_records = json.load(f)
            
            records = [r for r in all_records if r["name"] in remaining_names]
        
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    @time_it
    def run_backup(self, args: argparse.Namespace) -> None:
        """运行备份命令"""
        if args.action == "create":
            backup_path = self.create_backup(
                backup_name=args.name,
                compress=not args.no_compress,
                include_logs=args.include_logs
            )
            print(f"✅ 备份创建成功: {backup_path}")
            
        elif args.action == "list":
            backups = self.list_backups()
            if not backups:
                print("📭 没有找到备份")
                return
            
            print(f"📦 找到 {len(backups)} 个备份:")
            print("-" * 80)
            for i, backup in enumerate(backups, 1):
                print(f"{i:2d}. {backup['name']}")
                print(f"    类型: {backup.get('type', 'unknown')}")
                print(f"    大小: {backup.get('size_formatted', 'N/A')}")
                print(f"    时间: {backup.get('created_at', 'N/A')}")
                print(f"    路径: {backup.get('path', 'N/A')}")
                print()
        
        elif args.action == "restore":
            if not args.name:
                print("❌ 请指定要恢复的备份名称")
                return
            
            success = self.restore_backup(
                backup_name=args.name,
                overwrite=args.overwrite
            )
            
            if success:
                print(f"✅ 备份恢复成功: {args.name}")
            else:
                print(f"❌ 备份恢复失败: {args.name}")
        
        elif args.action == "cleanup":
            deleted = self.cleanup_old_backups(
                keep_count=args.keep_count,
                keep_days=args.keep_days
            )
            print(f"🧹 清理完成，删除了 {deleted} 个旧备份")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI宠物备份工具")
    subparsers = parser.add_subparsers(dest="action", help="操作命令")
    
    # 创建备份
    create_parser = subparsers.add_parser("create", help="创建备份")
    create_parser.add_argument("--name", "-n", help="备份名称")
    create_parser.add_argument("--no-compress", action="store_true", help="不压缩备份")
    create_parser.add_argument("--include-logs", action="store_true", help="包含日志文件")
    
    # 列出备份
    list_parser = subparsers.add_parser("list", help="列出备份")
    
    # 恢复备份
    restore_parser = subparsers.add_parser("restore", help="恢复备份")
    restore_parser.add_argument("name", help="备份名称")
    restore_parser.add_argument("--overwrite", "-f", action="store_true", help="覆盖现有文件")
    
    # 清理备份
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧备份")
    cleanup_parser.add_argument("--keep-count", "-c", type=int, default=5, help="保留最新备份数量")
    cleanup_parser.add_argument("--keep-days", "-d", type=int, default=30, help="保留天数")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        return
    
    try:
        backup_manager = BackupManager()
        backup_manager.run_backup(args)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()