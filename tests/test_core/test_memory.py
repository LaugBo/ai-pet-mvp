#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统测试
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.core.memory.storage import MemoryStorage
from src.core.memory.recall import MemoryRecall
from src.core.memory.optimizer import MemoryOptimizer


class TestMemoryStorage:
    """记忆存储测试"""
    
    def test_initialization(self, temp_data_dir):
        """测试初始化"""
        storage = MemoryStorage()
        
        assert storage.base_dir is not None
        assert storage.conversations_dir.exists()
        assert storage.moods_dir.exists()
        assert storage.summaries_dir.exists()
    
    def test_save_conversation(self, temp_data_dir):
        """测试保存对话"""
        storage = MemoryStorage()
        
        conversation_data = {
            "user": "你好",
            "ai": "你好！我是AI宠物。",
            "timestamp": "2024-01-01T00:00:00",
            "mood": "happy"
        }
        
        result = storage.save_conversation(conversation_data)
        
        assert result is True
        
        # 验证文件是否存在
        files = list(storage.conversations_dir.glob("*.json"))
        assert len(files) == 1
        
        # 验证文件内容
        with open(files[0], 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data["user"] == "你好"
        assert saved_data["ai"] == "你好！我是AI宠物。"
    
    def test_save_conversation_with_filename(self, temp_data_dir):
        """测试指定文件名保存对话"""
        storage = MemoryStorage()
        
        conversation_data = {
            "user": "测试消息",
            "ai": "测试回复"
        }
        
        filename = "test_conversation.json"
        result = storage.save_conversation(conversation_data, filename)
        
        assert result is True
        
        # 验证文件
        file_path = storage.conversations_dir / filename
        assert file_path.exists()
    
    def test_save_conversation_invalid_data(self, temp_data_dir):
        """测试保存无效数据"""
        storage = MemoryStorage()
        
        # 无效数据（非字典）
        result = storage.save_conversation("invalid data")
        
        assert result is False
    
    def test_load_conversation(self, temp_data_dir):
        """测试加载对话"""
        storage = MemoryStorage()
        
        # 先保存一个对话
        conversation_data = {
            "user": "测试加载",
            "ai": "测试回复",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        storage.save_conversation(conversation_data, "test_load.json")
        
        # 加载对话
        loaded_data = storage.load_conversation("test_load.json")
        
        assert loaded_data is not None
        assert loaded_data["user"] == "测试加载"
        assert loaded_data["ai"] == "测试回复"
    
    def test_load_nonexistent_conversation(self, temp_data_dir):
        """测试加载不存在的对话"""
        storage = MemoryStorage()
        
        loaded_data = storage.load_conversation("nonexistent.json")
        
        assert loaded_data is None
    
    def test_get_conversation_count(self, temp_data_dir):
        """测试获取对话数量"""
        storage = MemoryStorage()
        
        # 保存几个对话
        for i in range(3):
            storage.save_conversation({
                "user": f"消息{i}",
                "ai": f"回复{i}"
            })
        
        count = storage.get_conversation_count()
        
        assert count == 3
    
    def test_get_recent_conversations(self, temp_data_dir):
        """测试获取最近对话"""
        storage = MemoryStorage()
        
        # 保存几个对话
        for i in range(5):
            storage.save_conversation({
                "user": f"消息{i}",
                "ai": f"回复{i}",
                "timestamp": f"2024-01-0{i+1}T00:00:00"
            })
        
        conversations = storage.get_recent_conversations(limit=3)
        
        assert len(conversations) == 3
        # 应该按时间排序（最新的在前面）
        assert conversations[0]["user"] == "消息4"
    
    def test_delete_conversation(self, temp_data_dir):
        """测试删除对话"""
        storage = MemoryStorage()
        
        # 保存一个对话
        storage.save_conversation({"user": "测试", "ai": "测试"}, "test_delete.json")
        
        # 确认文件存在
        file_path = storage.conversations_dir / "test_delete.json"
        assert file_path.exists()
        
        # 删除
        result = storage.delete_conversation("test_delete.json")
        
        assert result is True
        assert not file_path.exists()
    
    def test_delete_nonexistent_conversation(self, temp_data_dir):
        """测试删除不存在的对话"""
        storage = MemoryStorage()
        
        result = storage.delete_conversation("nonexistent.json")
        
        assert result is False
    
    def test_save_mood(self, temp_data_dir):
        """测试保存心情"""
        storage = MemoryStorage()
        
        mood_data = {
            "mood": "happy",
            "reason": "用户说了开心的话",
            "confidence": 0.85,
            "timestamp": "2024-01-01T00:00:00"
        }
        
        result = storage.save_mood(mood_data)
        
        assert result is True
        
        # 验证文件
        files = list(storage.moods_dir.glob("*.json"))
        assert len(files) == 1
    
    def test_load_mood_history(self, temp_data_dir):
        """测试加载心情历史"""
        storage = MemoryStorage()
        
        # 保存几个心情记录
        for i in range(3):
            storage.save_mood({
                "mood": "happy",
                "reason": f"原因{i}",
                "confidence": 0.8 + i * 0.05
            })
        
        history = storage.load_mood_history(limit=2)
        
        assert len(history) == 2
    
    def test_save_summary(self, temp_data_dir):
        """测试保存摘要"""
        storage = MemoryStorage()
        
        summary_data = {
            "content": "这是一个对话摘要",
            "keywords": ["测试", "对话"],
            "timestamp": "2024-01-01T00:00:00"
        }
        
        result = storage.save_summary(summary_data)
        
        assert result is True
        
        # 验证文件
        files = list(storage.summaries_dir.glob("*.json"))
        assert len(files) == 1
    
    def test_cleanup_old_conversations(self, temp_data_dir):
        """测试清理旧对话"""
        storage = MemoryStorage()
        
        # 保存很多对话
        for i in range(15):
            storage.save_conversation({
                "user": f"消息{i}",
                "ai": f"回复{i}"
            })
        
        # 设置最大数量为10
        storage.max_conversations = 10
        
        # 清理
        storage.cleanup_old_conversations()
        
        # 应该只剩下10个
        count = storage.get_conversation_count()
        
        assert count == 10


class TestMemoryRecall:
    """记忆读取测试"""
    
    def test_initialization(self, temp_data_dir):
        """测试初始化"""
        storage = MemoryStorage()
        recall = MemoryRecall(storage)
        
        assert recall.storage == storage
    
    def test_search_conversations(self, temp_data_dir):
        """测试搜索对话"""
        storage = MemoryStorage()
        
        # 保存几个对话
        test_conversations = [
            {"user": "今天天气很好", "ai": "是的，适合出去玩"},
            {"user": "我喜欢编程", "ai": "编程很有趣"},
            {"user": "Python是最好的语言", "ai": "我同意"}
        ]
        
        for conv in test_conversations:
            storage.save_conversation(conv)
        
        recall = MemoryRecall(storage)
        
        # 搜索包含"编程"的对话
        results = recall.search_conversations("编程")
        
        assert len(results) >= 1
        assert any("编程" in str(conv) for conv in results)
    
    def test_search_conversations_no_results(self, temp_data_dir):
        """测试搜索无结果"""
        storage = MemoryStorage()
        recall = MemoryRecall(storage)
        
        results = recall.search_conversations("不存在的关键词")
        
        assert len(results) == 0
    
    def test_get_statistics(self, temp_data_dir):
        """测试获取统计信息"""
        storage = MemoryStorage()
        
        # 保存一些数据
        for i in range(3):
            storage.save_conversation({
                "user": f"用户消息{i}",
                "ai": f"AI回复{i}"
            })
        
        for i in range(2):
            storage.save_mood({
                "mood": "happy",
                "reason": f"原因{i}"
            })
        
        recall = MemoryRecall(storage)
        stats = recall.get_statistics()
        
        assert "conversation_count" in stats
        assert "mood_count" in stats
        assert "summary_count" in stats
        assert stats["conversation_count"] == 3
    
    def test_get_conversation_timeline(self, temp_data_dir):
        """测试获取对话时间线"""
        storage = MemoryStorage()
        
        # 保存带时间戳的对话
        timestamps = [
            "2024-01-01T10:00:00",
            "2024-01-01T12:00:00",
            "2024-01-02T10:00:00"
        ]
        
        for ts in timestamps:
            storage.save_conversation({
                "user": "测试",
                "ai": "测试",
                "timestamp": ts
            })
        
        recall = MemoryRecall(storage)
        timeline = recall.get_conversation_timeline()
        
        assert len(timeline) > 0
        assert "date" in timeline[0]
        assert "count" in timeline[0]


class TestMemoryOptimizer:
    """记忆优化器测试"""
    
    def test_initialization(self, temp_data_dir):
        """测试初始化"""
        storage = MemoryStorage()
        optimizer = MemoryOptimizer(storage)
        
        assert optimizer.storage == storage
    
    def test_generate_summary(self, temp_data_dir):
        """测试生成摘要"""
        storage = MemoryStorage()
        
        # 保存一个对话
        conversation = {
            "user": "今天天气很好，我想去公园玩。",
            "ai": "好主意！公园里空气新鲜，适合散步。",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        storage.save_conversation(conversation, "test_conv.json")
        
        optimizer = MemoryOptimizer(storage)
        
        # 生成摘要
        summary = optimizer.generate_summary("test_conv.json")
        
        assert summary is not None
        assert "content" in summary
        assert "keywords" in summary
        assert len(summary["keywords"]) > 0
    
    def test_generate_summary_nonexistent(self, temp_data_dir):
        """测试为不存在的对话生成摘要"""
        storage = MemoryStorage()
        optimizer = MemoryOptimizer(storage)
        
        summary = optimizer.generate_summary("nonexistent.json")
        
        assert summary is None
    
    def test_optimize_conversations(self, temp_data_dir):
        """测试优化对话"""
        storage = MemoryStorage()
        
        # 保存几个对话
        for i in range(3):
            storage.save_conversation({
                "user": f"用户消息{i}，今天天气很好。",
                "ai": f"AI回复{i}，是的，适合出门。"
            })
        
        optimizer = MemoryOptimizer(storage)
        
        # 优化所有对话
        result = optimizer.optimize_conversations()
        
        assert "processed" in result
        assert "generated" in result
        assert result["processed"] == 3
    
    def test_extract_keywords(self):
        """测试提取关键词"""
        storage = Mock()
        optimizer = MemoryOptimizer(storage)
        
        text = "今天天气很好，我想去公园玩。公园里有很多花和树。"
        
        keywords = optimizer._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # 中文关键词应该被提取
        assert any(keyword in text for keyword in keywords)
    
    def test_compress_conversation(self):
        """测试压缩对话"""
        storage = Mock()
        optimizer = MemoryOptimizer(storage)
        
        conversation = {
            "user": "这是一个很长的用户消息，包含了很多不必要的细节和重复的内容。",
            "ai": "这是一个很长的AI回复，也包含了很多不必要的内容。",
            "timestamp": "2024-01-01T00:00:00",
            "extra_field": "额外信息"
        }
        
        compressed = optimizer._compress_conversation(conversation)
        
        assert "user" in compressed
        assert "ai" in compressed
        assert "timestamp" in compressed
        # 额外字段应该被移除
        assert "extra_field" not in compressed
        # 内容应该被缩短
        assert len(compressed["user"]) <= len(conversation["user"])
    
    def test_backup_memory(self, temp_data_dir):
        """测试备份记忆"""
        storage = MemoryStorage()
        
        # 保存一些数据
        for i in range(2):
            storage.save_conversation({
                "user": f"消息{i}",
                "ai": f"回复{i}"
            })
        
        optimizer = MemoryOptimizer(storage)
        
        # 创建备份
        backup_path = optimizer.create_backup()
        
        assert backup_path is not None
        assert backup_path.exists()
        
        # 备份应该包含文件
        import zipfile
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            file_list = zipf.namelist()
            assert any("conversations" in f for f in file_list)
    
    def test_restore_from_backup(self, temp_data_dir):
        """测试从备份恢复"""
        storage = MemoryStorage()
        optimizer = MemoryOptimizer(storage)
        
        # 先创建备份
        backup_path = optimizer.create_backup()
        
        # 清除当前数据
        for file in storage.conversations_dir.glob("*.json"):
            file.unlink()
        
        # 从备份恢复
        result = optimizer.restore_from_backup(backup_path)
        
        assert result is True
        
        # 数据应该被恢复
        count = storage.get_conversation_count()
        assert count > 0