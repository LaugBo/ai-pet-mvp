#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

from src.core.ai.adapter import AIManager, AIAdapter
from src.core.ai.connector import OllamaConnector


class TestOllamaConnector:
    """Ollama连接器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        connector = OllamaConnector(ip="localhost", port=11434, model="test-model")
        
        assert connector.ip == "localhost"
        assert connector.port == 11434
        assert connector.model == "test-model"
        assert connector.timeout == 60
        assert connector.base_url == "http://localhost:11434"
        assert not connector.is_connected
    
    def test_generate_url(self):
        """测试URL生成"""
        connector = OllamaConnector(ip="192.168.1.100", port=8080, model="test")
        
        assert connector.base_url == "http://192.168.1.100:8080"
        assert connector.generate_url == "http://192.168.1.100:8080/api/generate"
        assert connector.models_url == "http://192.168.1.100:8080/api/tags"
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """测试成功生成"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test-model",
            "response": "测试响应",
            "done": True
        }
        mock_post.return_value = mock_response
        
        connector = OllamaConnector(ip="localhost", port=11434, model="test-model")
        
        # 测试生成
        response = connector.generate("你好")
        
        assert response == "测试响应"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_failure(self, mock_post):
        """测试生成失败"""
        mock_post.side_effect = Exception("连接失败")
        
        connector = OllamaConnector(ip="localhost", port=11434, model="test-model")
        
        # 应该返回错误信息
        response = connector.generate("你好")
        assert "错误" in response or "失败" in response
    
    @patch('requests.get')
    def test_check_connection_success(self, mock_get):
        """测试连接检查成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        connector = OllamaConnector(ip="localhost", port=11434, model="test-model")
        
        assert connector.check_connection() is True
    
    @patch('requests.get')
    def test_check_connection_failure(self, mock_get):
        """测试连接检查失败"""
        mock_get.side_effect = Exception("连接失败")
        
        connector = OllamaConnector(ip="localhost", port=11434, model="test-model")
        
        assert connector.check_connection() is False


class TestAIAdapter:
    """AI适配器测试"""
    
    def test_adapter_creation(self):
        """测试适配器创建"""
        adapter = AIAdapter(ai_type="test")
        
        assert adapter.ai_type == "test"
        assert adapter.is_connected is False
        assert adapter.model is None
    
    def test_invalid_adapter_type(self):
        """测试无效的适配器类型"""
        with pytest.raises(ValueError):
            AIAdapter(ai_type="invalid_type")
    
    @patch('src.core.ai.connector.OllamaConnector')
    def test_create_ollama_adapter(self, mock_connector):
        """测试创建Ollama适配器"""
        mock_connector_instance = Mock()
        mock_connector.return_value = mock_connector_instance
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        adapter = AIAdapter.create_adapter(config)
        
        assert adapter.ai_type == "ollama"
        mock_connector.assert_called_once_with(
            ip="localhost",
            port=11434,
            model="test-model",
            timeout=60
        )
    
    def test_unsupported_adapter_type(self):
        """测试不支持的适配器类型"""
        config = {
            "adapter_type": "unsupported",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        with pytest.raises(ValueError, match="不支持的AI类型"):
            AIAdapter.create_adapter(config)


class TestAIManager:
    """AI管理器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        
        assert manager.config == config
        assert manager.adapter is None
        assert not manager.is_connected
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_connect_success(self, mock_create_adapter):
        """测试连接成功"""
        # 模拟适配器
        mock_adapter = Mock()
        mock_adapter.ai_type = "ollama"
        mock_adapter.model = "test-model"
        mock_adapter.connect.return_value = True
        mock_adapter.is_connected = True
        mock_create_adapter.return_value = mock_adapter
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        result = manager.connect()
        
        assert result is True
        assert manager.is_connected is True
        assert manager.adapter == mock_adapter
        mock_create_adapter.assert_called_once_with(config)
        mock_adapter.connect.assert_called_once()
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_connect_failure(self, mock_create_adapter):
        """测试连接失败"""
        mock_adapter = Mock()
        mock_adapter.connect.return_value = False
        mock_create_adapter.return_value = mock_adapter
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        result = manager.connect()
        
        assert result is False
        assert manager.is_connected is False
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_generate_response(self, mock_create_adapter):
        """测试生成响应"""
        mock_adapter = Mock()
        mock_adapter.is_connected = True
        mock_adapter.generate.return_value = "测试AI响应"
        mock_create_adapter.return_value = mock_adapter
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        manager.connect()  # 连接到模拟适配器
        
        response = manager.generate_response("你好")
        
        assert response == "测试AI响应"
        mock_adapter.generate.assert_called_once_with("你好", None)
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_generate_without_connection(self, mock_create_adapter):
        """测试未连接时生成响应"""
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        # 不调用connect()
        
        response = manager.generate_response("你好")
        
        assert "未连接" in response or "失败" in response
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_disconnect(self, mock_create_adapter):
        """测试断开连接"""
        mock_adapter = Mock()
        mock_create_adapter.return_value = mock_adapter
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        manager.connect()
        
        manager.disconnect()
        
        mock_adapter.disconnect.assert_called_once()
        assert manager.adapter is None
        assert not manager.is_connected
    
    def test_get_status(self):
        """测试获取状态"""
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        
        status = manager.get_status()
        
        assert "type" in status
        assert "connected" in status
        assert "model" in status
        assert status["type"] == "ollama"
        assert status["connected"] is False
    
    @patch('src.core.ai.adapter.AIAdapter.create_adapter')
    def test_get_status_connected(self, mock_create_adapter):
        """测试获取已连接状态"""
        mock_adapter = Mock()
        mock_adapter.ai_type = "ollama"
        mock_adapter.model = "test-model"
        mock_adapter.is_connected = True
        mock_create_adapter.return_value = mock_adapter
        
        config = {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "test-model"
        }
        
        manager = AIManager(config)
        manager.connect()
        
        status = manager.get_status()
        
        assert status["connected"] is True
        assert status["model"] == "test-model"