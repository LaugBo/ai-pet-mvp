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