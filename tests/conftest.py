#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件
为pytest测试提供共享的fixture和配置
"""

import os
import sys
import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_dir():
    """返回项目根目录"""
    return project_root


@pytest.fixture
def temp_dir():
    """临时目录fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_data_dir(temp_dir):
    """临时数据目录fixture"""
    data_dir = temp_dir / "data"
    data_dir.mkdir()
    (data_dir / "config").mkdir()
    (data_dir / "memory").mkdir()
    (data_dir / "memory" / "conversations").mkdir(parents=True)
    (data_dir / "memory" / "moods").mkdir(parents=True)
    (data_dir / "memory" / "summaries").mkdir(parents=True)
    return data_dir


@pytest.fixture
def sample_config(temp_data_dir):
    """示例配置文件fixture"""
    config_dir = temp_data_dir / "config"
    
    # AI配置
    ai_config = {
        "active_profile": "test_ollama",
        "profiles": {
            "test_ollama": {
                "name": "测试Ollama",
                "type": "ollama",
                "base_url": "http://localhost:11434",
                "model": "test-model:latest",
                "timeout": 30
            }
        }
    }
    
    ai_file = config_dir / "ai_profiles.json"
    with open(ai_file, 'w', encoding='utf-8') as f:
        json.dump(ai_config, f, ensure_ascii=False, indent=2)
    
    # 应用设置
    app_config = {
        "window": {
            "width": 1000,
            "height": 700
        },
        "chat": {
            "max_history": 100,
            "auto_scroll": True
        },
        "memory": {
            "max_conversations": 1000,
            "auto_summarize": True
        }
    }
    
    app_file = config_dir / "settings.json"
    with open(app_file, 'w', encoding='utf-8') as f:
        json.dump(app_config, f, ensure_ascii=False, indent=2)
    
    # 心情规则
    mood_config = {
        "moods": {
            "happy": {
                "keywords": ["开心", "高兴", "喜欢", "爱", "棒", "好"],
                "weight": 1.0
            },
            "sad": {
                "keywords": ["伤心", "难过", "悲伤", "哭", "不好", "讨厌"],
                "weight": 1.0
            },
            "neutral": {
                "keywords": [],
                "weight": 0.5
            }
        },
        "default_mood": "neutral"
    }
    
    mood_file = config_dir / "mood_rules.json"
    with open(mood_file, 'w', encoding='utf-8') as f:
        json.dump(mood_config, f, ensure_ascii=False, indent=2)
    
    return config_dir


@pytest.fixture
def mock_ai_response():
    """模拟AI响应fixture"""
    return {
        "model": "test-model:latest",
        "created_at": "2024-01-01T00:00:00.000000Z",
        "message": {
            "role": "assistant",
            "content": "这是一个测试AI响应。"
        },
        "done": True,
        "total_duration": 5000000000,
        "load_duration": 1000000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 1000000000,
        "eval_count": 20,
        "eval_duration": 3000000000
    }


@pytest.fixture
def mock_ai_adapter():
    """模拟AI适配器fixture"""
    adapter = Mock()
    adapter.ai_type = "test"
    adapter.is_connected = True
    adapter.model = "test-model:latest"
    
    def mock_generate(prompt, **kwargs):
        return f"AI回复: {prompt[:20]}..."
    
    adapter.generate = Mock(side_effect=mock_generate)
    adapter.connect = Mock(return_value=True)
    adapter.disconnect = Mock()
    
    return adapter


@pytest.fixture
def mock_memory_storage(temp_dir):
    """模拟记忆存储fixture"""
    storage = Mock()
    storage.base_dir = temp_dir / "memory"
    storage.base_dir.mkdir(parents=True, exist_ok=True)
    
    storage.save_conversation = Mock(return_value=True)
    storage.load_conversation = Mock(return_value={})
    storage.get_conversation_count = Mock(return_value=0)
    storage.delete_conversation = Mock(return_value=True)
    
    return storage


@pytest.fixture
def mock_mood_manager():
    """模拟心情管理器fixture"""
    from src.core.mood.manager import MoodType
    
    manager = Mock()
    manager.current_mood = MoodType.HAPPY
    manager.mood_history = []
    
    def mock_analyze(text):
        from src.core.mood.analyzer import MoodResult
        return MoodResult(
            mood_type=MoodType.HAPPY,
            confidence=0.8,
            reason="测试分析"
        )
    
    manager.analyze_text = Mock(side_effect=mock_analyze)
    manager.update_mood = Mock()
    manager.save_current_mood = Mock()
    manager.load_mood_history = Mock(return_value=[])
    
    return manager


@pytest.fixture
def mock_config_manager(sample_config):
    """模拟配置管理器fixture"""
    manager = Mock()
    manager.config_dir = sample_config
    
    def mock_load(config_name):
        config_file = sample_config / config_name
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    manager.load_config = Mock(side_effect=mock_load)
    manager.save_config = Mock(return_value=True)
    manager.get_config_path = Mock(return_value=str(sample_config))
    
    return manager


@pytest.fixture
def qt_app():
    """Qt应用fixture（用于UI测试）"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    yield app


@pytest.fixture
def clean_imports():
    """清理导入的模块（用于隔离测试）"""
    import_modules = set(sys.modules.keys())
    yield
    # 清理测试期间导入的模块
    new_modules = set(sys.modules.keys()) - import_modules
    for module in new_modules:
        if module.startswith('src.') or module.startswith('tests.'):
            del sys.modules[module]


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, temp_dir):
    """设置测试环境（自动使用）"""
    # 设置环境变量
    monkeypatch.setenv('AI_PET_TEST', 'true')
    
    # 临时目录
    test_data_dir = temp_dir / "data"
    monkeypatch.setattr('src.utils.config.DATA_DIR', test_data_dir)
    
    # 日志级别设为警告，减少测试输出
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    yield
    
    # 测试后清理
    pass