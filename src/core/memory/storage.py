# 记忆存储系统
# 功能：负责存储和读取对话记忆

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

class MemoryStorage:
    """
    记忆存储类
    管理对话记忆的存储和读取
    """
    
    def __init__(self, storage_path: str = None):
        """
        初始化记忆存储
        
        参数:
            storage_path: 存储路径，默认为 data/memory/
        """
        if storage_path is None:
            # 默认存储路径
            self.storage_path = Path(__file__).parent.parent.parent.parent / "data" / "memory"
        else:
            self.storage_path = Path(storage_path)
        
        # 确保目录存在
        self.conversations_path = self.storage_path / "conversations"
        self.summaries_path = self.storage_path / "summaries"
        self.moods_path = self.storage_path / "moods"
        
        self._ensure_directories()
        
        print(f"记忆存储初始化完成")
        print(f"存储路径: {self.storage_path}")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        for path in [self.conversations_path, self.summaries_path, self.moods_path]:
            path.mkdir(parents=True, exist_ok=True)
            print(f"确保目录存在: {path}")
    
    def save_conversation(self, 
                         conversation_id: str, 
                         messages: List[Dict[str, Any]],
                         metadata: Dict[str, Any] = None) -> bool:
        """
        保存对话记录
        
        参数:
            conversation_id: 对话ID
            messages: 消息列表
            metadata: 元数据
            
        返回:
            是否保存成功
        """
        try:
            # 准备数据
            data = {
                "conversation_id": conversation_id,
                "timestamp": time.time(),
                "date": datetime.now().isoformat(),
                "message_count": len(messages),
                "messages": messages,
                "metadata": metadata or {}
            }
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conv_{conversation_id}_{timestamp}.json"
            filepath = self.conversations_path / filename
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 对话保存成功: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存对话失败: {e}")
            return False
    
    def load_conversation(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载对话记录
        
        参数:
            filename: 文件名
            
        返回:
            对话数据
        """
        try:
            filepath = self.conversations_path / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ 对话加载成功: {filename}")
            return data
            
        except Exception as e:
            print(f"❌ 加载对话失败: {filename} - {e}")
            return None
    
    def list_conversations(self, 
                          limit: int = None, 
                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        列出所有对话记录
        
        参数:
            limit: 限制数量
            offset: 偏移量
            
        返回:
            对话列表
        """
        try:
            conversations = []
            
            # 获取所有对话文件
            files = sorted(self.conversations_path.glob("conv_*.json"), 
                          key=os.path.getmtime, 
                          reverse=True)
            
            # 应用偏移和限制
            if offset > 0:
                files = files[offset:]
            
            if limit:
                files = files[:limit]
            
            # 加载文件基本信息
            for filepath in files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conversation_info = {
                        "filename": filepath.name,
                        "conversation_id": data.get("conversation_id", "unknown"),
                        "timestamp": data.get("timestamp", 0),
                        "date": data.get("date", ""),
                        "message_count": data.get("message_count", 0),
                        "file_size": filepath.stat().st_size
                    }
                    
                    conversations.append(conversation_info)
                    
                except Exception as e:
                    print(f"❌ 读取对话文件失败: {filepath.name} - {e}")
            
            print(f"✅ 列出 {len(conversations)} 个对话")
            return conversations
            
        except Exception as e:
            print(f"❌ 列出对话失败: {e}")
            return []
    
    def save_summary(self, 
                    conversation_id: str, 
                    summary: Dict[str, Any]) -> bool:
        """
        保存对话摘要
        
        参数:
            conversation_id: 对话ID
            summary: 摘要数据
            
        返回:
            是否保存成功
        """
        try:
            # 准备数据
            data = {
                "conversation_id": conversation_id,
                "timestamp": time.time(),
                "date": datetime.now().isoformat(),
                "summary": summary
            }
            
            # 生成文件名
            filename = f"summary_{conversation_id}.json"
            filepath = self.summaries_path / filename
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 摘要保存成功: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存摘要失败: {e}")
            return False
    
    def load_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        加载对话摘要
        
        参数:
            conversation_id: 对话ID
            
        返回:
            摘要数据
        """
        try:
            filename = f"summary_{conversation_id}.json"
            filepath = self.summaries_path / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ 摘要加载成功: {conversation_id}")
            return data
            
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"❌ 加载摘要失败: {conversation_id} - {e}")
            return None
    
    def save_mood_record(self, 
                        mood_data: Dict[str, Any]) -> bool:
        """
        保存心情记录
        
        参数:
            mood_data: 心情数据
            
        返回:
            是否保存成功
        """
        try:
            # 添加时间戳
            mood_data["timestamp"] = time.time()
            mood_data["date"] = datetime.now().isoformat()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"mood_{timestamp}.json"
            filepath = self.moods_path / filename
            
            # 检查文件是否存在
            if filepath.exists():
                # 读取现有数据
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
                
                existing_data.append(mood_data)
                data_to_save = existing_data
            else:
                data_to_save = [mood_data]
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 心情记录保存成功: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 保存心情记录失败: {e}")
            return False
    
    def load_mood_records(self, date: str = None) -> List[Dict[str, Any]]:
        """
        加载心情记录
        
        参数:
            date: 日期 (YYYYMMDD)，None则加载今天
            
        返回:
            心情记录列表
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            
            filename = f"mood_{date}.json"
            filepath = self.moods_path / filename
            
            if not filepath.exists():
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            else:
                return [data]
                
        except Exception as e:
            print(f"❌ 加载心情记录失败: {e}")
            return []
    
    def cleanup_old_files(self, 
                         days_to_keep: int = 30) -> int:
        """
        清理旧文件
        
        参数:
            days_to_keep: 保留天数
            
        返回:
            删除的文件数量
        """
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            # 清理对话文件
            for filepath in self.conversations_path.glob("*.json"):
                if filepath.stat().st_mtime < cutoff_time:
                    try:
                        filepath.unlink()
                        deleted_count += 1
                        print(f"🗑️ 删除旧文件: {filepath.name}")
                    except Exception as e:
                        print(f"❌ 删除文件失败: {filepath.name} - {e}")
            
            print(f"✅ 清理完成，删除了 {deleted_count} 个文件")
            return deleted_count
            
        except Exception as e:
            print(f"❌ 清理文件失败: {e}")
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储信息
        
        返回:
            存储信息字典
        """
        try:
            info = {
                "conversations": {
                    "count": len(list(self.conversations_path.glob("*.json"))),
                    "path": str(self.conversations_path)
                },
                "summaries": {
                    "count": len(list(self.summaries_path.glob("*.json"))),
                    "path": str(self.summaries_path)
                },
                "moods": {
                    "count": len(list(self.moods_path.glob("*.json"))),
                    "path": str(self.moods_path)
                },
                "total_size": {
                    "bytes": 0,
                    "human_readable": "0 B"
                }
            }
            
            # 计算总大小
            total_bytes = 0
            for path in [self.conversations_path, self.summaries_path, self.moods_path]:
                for filepath in path.glob("*.json"):
                    total_bytes += filepath.stat().st_size
            
            # 转换为人类可读格式
            bytes_copy = total_bytes
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_copy < 1024.0:
                    info["total_size"]["human_readable"] = f"{bytes_copy:.1f} {unit}"
                    break
                bytes_copy /= 1024.0
            
            info["total_size"]["bytes"] = total_bytes
            
            return info
            
        except Exception as e:
            print(f"❌ 获取存储信息失败: {e}")
            return {}
    
    def generate_conversation_id(self, seed: str = None) -> str:
        """
        生成对话ID
        
        参数:
            seed: 种子字符串
            
        返回:
            对话ID
        """
        if seed is None:
            seed = str(time.time()) + str(os.urandom(16))
        
        # 使用SHA256生成唯一ID
        hash_obj = hashlib.sha256(seed.encode())
        return hash_obj.hexdigest()[:16]

# 使用示例
if __name__ == "__main__":
    print("记忆存储系统测试")
    print("=" * 50)
    
    # 创建存储实例
    storage = MemoryStorage()
    
    # 测试存储信息
    info = storage.get_storage_info()
    print(f"存储信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
    
    # 测试生成对话ID
    conv_id = storage.generate_conversation_id()
    print(f"生成的对话ID: {conv_id}")
    
    # 测试保存对话
    test_messages = [
        {"role": "user", "content": "你好", "timestamp": time.time()},
        {"role": "assistant", "content": "你好！我是AI助手。", "timestamp": time.time()}
    ]
    
    success = storage.save_conversation(conv_id, test_messages, {"test": True})
    if success:
        print("✅ 对话保存测试通过")
    
    # 测试列出对话
    conversations = storage.list_conversations(limit=5)
    print(f"最近的对话: {len(conversations)} 个")
    
    print("=" * 50)
    print("记忆存储系统测试完成")