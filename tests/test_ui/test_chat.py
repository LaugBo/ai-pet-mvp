#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天管理器测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import time

from src.ui.chat import ChatManager
from src.core.ai.adapter import AIManager


class TestChatManager:
    """聊天管理器测试"""
    
    def test_initialization(self, mock_config_manager, mock_ai_adapter):
        """测试初始化"""
        # 创建AI管理器
        ai_manager = Mock()
        ai_manager.adapter = mock_ai_adapter
        ai_manager.is_connected = False
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        assert chat_manager.config_manager == mock_config_manager
        assert chat_manager.ai_manager == ai_manager
        assert chat_manager.is_connected is False
        assert chat_manager.conversation_history == []
    
    def test_initialization_no_ai_manager(self, mock_config_manager):
        """测试无AI管理器初始化"""
        chat_manager = ChatManager(mock_config_manager, None)
        
        assert chat_manager.ai_manager is None
        assert chat_manager.is_connected is False
    
    def test_connect_ai_success(self, mock_config_manager):
        """测试成功连接AI"""
        # 模拟AI管理器
        ai_manager = Mock()
        ai_manager.connect.return_value = True
        ai_manager.is_connected = True
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 连接AI
        result = chat_manager.connect_ai()
        
        assert result is True
        assert chat_manager.is_connected is True
        ai_manager.connect.assert_called_once()
    
    def test_connect_ai_failure(self, mock_config_manager):
        """测试连接AI失败"""
        ai_manager = Mock()
        ai_manager.connect.return_value = False
        ai_manager.is_connected = False
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        result = chat_manager.connect_ai()
        
        assert result is False
        assert chat_manager.is_connected is False
    
    def test_connect_ai_no_ai_manager(self, mock_config_manager):
        """测试无AI管理器时连接"""
        chat_manager = ChatManager(mock_config_manager, None)
        
        result = chat_manager.connect_ai()
        
        assert result is False
        assert chat_manager.is_connected is False
    
    def test_disconnect(self, mock_config_manager):
        """测试断开连接"""
        ai_manager = Mock()
        ai_manager.disconnect = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        
        # 断开连接
        chat_manager.disconnect()
        
        assert chat_manager.is_connected is False
        ai_manager.disconnect.assert_called_once()
    
    def test_send_message_success(self, mock_config_manager):
        """测试成功发送消息"""
        # 模拟AI管理器
        ai_manager = Mock()
        ai_manager.is_connected = True
        ai_manager.generate_response.return_value = "AI回复消息"
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        
        # 模拟信号
        chat_manager.response_received = Mock()
        chat_manager.error_occurred = Mock()
        
        # 发送消息
        chat_manager.send_message("用户消息")
        
        # 应该生成响应
        ai_manager.generate_response.assert_called_with("用户消息", None)
        
        # 应该发出响应信号
        chat_manager.response_received.emit.assert_called_with("AI回复消息")
        
        # 历史记录应该更新
        assert len(chat_manager.conversation_history) == 1
        assert chat_manager.conversation_history[0]["user"] == "用户消息"
        assert chat_manager.conversation_history[0]["ai"] == "AI回复消息"
    
    def test_send_message_not_connected(self, mock_config_manager):
        """测试未连接时发送消息"""
        ai_manager = Mock()
        ai_manager.is_connected = False
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 模拟信号
        chat_manager.error_occurred = Mock()
        
        # 发送消息
        chat_manager.send_message("用户消息")
        
        # 应该发出错误信号
        chat_manager.error_occurred.emit.assert_called_with("AI未连接，请先连接AI")
        
        # 历史记录不应该更新
        assert len(chat_manager.conversation_history) == 0
    
    def test_send_message_ai_error(self, mock_config_manager):
        """测试AI生成错误"""
        ai_manager = Mock()
        ai_manager.is_connected = True
        ai_manager.generate_response.side_effect = Exception("AI生成失败")
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        
        # 模拟信号
        chat_manager.error_occurred = Mock()
        
        # 发送消息
        chat_manager.send_message("用户消息")
        
        # 应该发出错误信号
        chat_manager.error_occurred.emit.assert_called()
        
        # 错误消息应该包含"AI生成失败"
        error_msg = chat_manager.error_occurred.emit.call_args[0][0]
        assert "AI生成失败" in error_msg
    
    def test_send_message_empty(self, mock_config_manager):
        """测试发送空消息"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 模拟信号
        chat_manager.error_occurred = Mock()
        
        # 发送空消息
        chat_manager.send_message("")
        
        # 应该发出错误信号
        chat_manager.error_occurred.emit.assert_called_with("消息不能为空")
    
    def test_send_message_whitespace(self, mock_config_manager):
        """测试发送空白消息"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        chat_manager.error_occurred = Mock()
        
        chat_manager.send_message("   ")
        
        chat_manager.error_occurred.emit.assert_called_with("消息不能为空")
    
    def test_get_conversation_history(self, mock_config_manager):
        """测试获取对话历史"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 添加一些历史记录
        chat_manager.conversation_history = [
            {"user": "消息1", "ai": "回复1", "timestamp": "2024-01-01T10:00:00"},
            {"user": "消息2", "ai": "回复2", "timestamp": "2024-01-01T11:00:00"}
        ]
        
        history = chat_manager.get_conversation_history()
        
        assert len(history) == 2
        assert history[0]["user"] == "消息1"
        assert history[1]["user"] == "消息2"
    
    def test_get_conversation_history_with_limit(self, mock_config_manager):
        """测试获取有限数量的对话历史"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 添加多个历史记录
        for i in range(10):
            chat_manager.conversation_history.append({
                "user": f"消息{i}",
                "ai": f"回复{i}",
                "timestamp": f"2024-01-01T{i:02d}:00:00"
            })
        
        # 获取最近5条
        history = chat_manager.get_conversation_history(limit=5)
        
        assert len(history) == 5
        # 应该返回最新的5条
        assert history[0]["user"] == "消息9"
        assert history[4]["user"] == "消息5"
    
    def test_clear_conversation_history(self, mock_config_manager):
        """测试清空对话历史"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 添加历史记录
        chat_manager.conversation_history = [
            {"user": "消息1", "ai": "回复1"},
            {"user": "消息2", "ai": "回复2"}
        ]
        
        # 清空历史
        chat_manager.clear_conversation_history()
        
        assert len(chat_manager.conversation_history) == 0
    
    def test_save_conversation(self, mock_config_manager, mock_memory_storage):
        """测试保存对话"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 设置记忆存储
        chat_manager.memory_storage = mock_memory_storage
        
        # 添加对话历史
        chat_manager.conversation_history = [
            {"user": "消息1", "ai": "回复1", "timestamp": "2024-01-01T10:00:00"},
            {"user": "消息2", "ai": "回复2", "timestamp": "2024-01-01T11:00:00"}
        ]
        
        # 保存对话
        chat_manager.save_conversation()
        
        # 应该调用了记忆存储
        assert mock_memory_storage.save_conversation.call_count == 2
    
    def test_save_conversation_no_storage(self, mock_config_manager):
        """测试无存储时保存对话"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.memory_storage = None
        
        # 添加历史记录
        chat_manager.conversation_history = [{"user": "消息", "ai": "回复"}]
        
        # 应该不会崩溃
        chat_manager.save_conversation()
    
    def test_load_conversation_history(self, mock_config_manager, mock_memory_storage):
        """测试加载对话历史"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 设置记忆存储
        chat_manager.memory_storage = mock_memory_storage
        
        # 模拟存储返回的对话
        mock_conversations = [
            {"user": "保存的消息1", "ai": "保存的回复1"},
            {"user": "保存的消息2", "ai": "保存的回复2"}
        ]
        mock_memory_storage.get_recent_conversations.return_value = mock_conversations
        
        # 加载对话历史
        loaded = chat_manager.load_conversation_history(limit=5)
        
        assert loaded == 2
        assert len(chat_manager.conversation_history) == 2
        mock_memory_storage.get_recent_conversations.assert_called_with(5)
    
    def test_load_conversation_history_no_storage(self, mock_config_manager):
        """测试无存储时加载对话历史"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.memory_storage = None
        
        # 应该返回0
        loaded = chat_manager.load_conversation_history()
        
        assert loaded == 0
    
    def test_set_memory_storage(self, mock_config_manager):
        """测试设置记忆存储"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 模拟记忆存储
        memory_storage = Mock()
        
        # 设置记忆存储
        chat_manager.set_memory_storage(memory_storage)
        
        assert chat_manager.memory_storage == memory_storage
    
    def test_get_status(self, mock_config_manager):
        """测试获取状态"""
        ai_manager = Mock()
        ai_manager.is_connected = True
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        
        status = chat_manager.get_status()
        
        assert "connected" in status
        assert "history_count" in status
        assert status["connected"] is True
        assert status["history_count"] == 0
    
    def test_get_status_not_connected(self, mock_config_manager):
        """测试获取未连接状态"""
        ai_manager = Mock()
        ai_manager.is_connected = False
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = False
        
        status = chat_manager.get_status()
        
        assert status["connected"] is False
    
    def test_update_status_signal(self, mock_config_manager):
        """测试更新状态信号"""
        ai_manager = Mock()
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        
        # 模拟信号
        chat_manager.status_changed = Mock()
        
        # 触发状态更新
        chat_manager._update_status("测试状态", True)
        
        # 应该发出信号
        chat_manager.status_changed.emit.assert_called_with("测试状态", True)
    
    def test_auto_save_conversation(self, mock_config_manager, mock_memory_storage):
        """测试自动保存对话"""
        ai_manager = Mock()
        ai_manager.is_connected = True
        ai_manager.generate_response.return_value = "AI回复"
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        chat_manager.memory_storage = mock_memory_storage
        
        # 设置自动保存
        chat_manager.auto_save = True
        
        # 模拟信号
        chat_manager.response_received = Mock()
        
        # 发送多条消息
        for i in range(3):
            chat_manager.send_message(f"消息{i}")
        
        # 等待自动保存触发
        time.sleep(0.1)
        
        # 记忆存储应该被调用
        assert mock_memory_storage.save_conversation.call_count >= 1
    
    def test_auto_save_disabled(self, mock_config_manager, mock_memory_storage):
        """测试禁用自动保存"""
        ai_manager = Mock()
        ai_manager.is_connected = True
        ai_manager.generate_response.return_value = "AI回复"
        
        chat_manager = ChatManager(mock_config_manager, ai_manager)
        chat_manager.is_connected = True
        chat_manager.memory_storage = mock_memory_storage
        
        # 禁用自动保存
        chat_manager.auto_save = False
        
        chat_manager.response_received = Mock()
        
        # 发送消息
        chat_manager.send_message("测试消息")
        
        # 记忆存储不应该被调用
        mock_memory_storage.save_conversation.assert_not_called()