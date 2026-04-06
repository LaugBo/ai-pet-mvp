#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心情系统测试
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.core.mood.analyzer import MoodAnalyzer, MoodResult, MoodType
from src.core.mood.manager import MoodManager
from src.core.mood.images import MoodImageManager


class TestMoodAnalyzer:
    """心情分析器测试"""
    
    def test_initialization(self, sample_config):
        """测试初始化"""
        analyzer = MoodAnalyzer()
        
        assert analyzer.rules is not None
        assert "happy" in analyzer.rules
        assert "sad" in analyzer.rules
        assert "neutral" in analyzer.rules
    
    def test_load_rules_from_file(self, sample_config):
        """测试从文件加载规则"""
        rules_file = sample_config / "mood_rules.json"
        
        analyzer = MoodAnalyzer()
        # 重新从文件加载规则
        analyzer._load_rules(str(rules_file))
        
        assert analyzer.rules is not None
        assert "happy" in analyzer.rules
        assert "sad" in analyzer.rules
    
    def test_load_rules_invalid_file(self):
        """测试加载无效规则文件"""
        analyzer = MoodAnalyzer()
        
        # 不存在的文件应该使用默认规则
        analyzer._load_rules("nonexistent.json")
        
        assert analyzer.rules is not None
        assert len(analyzer.rules) > 0
    
    def test_analyze_positive_text(self):
        """测试分析积极文本"""
        analyzer = MoodAnalyzer()
        
        text = "我今天很开心，天气真好！"
        result = analyzer.analyze(text)
        
        assert isinstance(result, MoodResult)
        assert result.mood_type == MoodType.HAPPY
        assert result.confidence > 0.5
        assert result.reason is not None
    
    def test_analyze_negative_text(self):
        """测试分析消极文本"""
        analyzer = MoodAnalyzer()
        
        text = "我很难过，今天的事情让我伤心。"
        result = analyzer.analyze(text)
        
        assert result.mood_type == MoodType.SAD
        assert result.confidence > 0.5
    
    def test_analyze_neutral_text(self):
        """测试分析中性文本"""
        analyzer = MoodAnalyzer()
        
        text = "今天星期三，普通的一天。"
        result = analyzer.analyze(text)
        
        assert result.mood_type == MoodType.NEUTRAL
    
    def test_analyze_mixed_text(self):
        """测试分析混合情绪文本"""
        analyzer = MoodAnalyzer()
        
        text = "虽然今天有点难过，但也有开心的事情。"
        result = analyzer.analyze(text)
        
        # 应该有一种主要情绪
        assert result.mood_type in [MoodType.HAPPY, MoodType.SAD, MoodType.NEUTRAL]
        assert result.confidence > 0
    
    def test_analyze_empty_text(self):
        """测试分析空文本"""
        analyzer = MoodAnalyzer()
        
        result = analyzer.analyze("")
        
        assert result.mood_type == MoodType.NEUTRAL
        assert result.confidence == 1.0
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        analyzer = MoodAnalyzer()
        
        # 测试高置信度
        mood_scores = {"happy": 0.8, "sad": 0.1, "neutral": 0.1}
        confidence = analyzer._calculate_confidence(mood_scores)
        
        assert 0 <= confidence <= 1
        assert confidence > 0.5
        
        # 测试低置信度
        mood_scores = {"happy": 0.33, "sad": 0.33, "neutral": 0.34}
        confidence = analyzer._calculate_confidence(mood_scores)
        
        assert confidence < 0.5
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        analyzer = MoodAnalyzer()
        
        text = "今天天气很好，我很开心，想去公园玩。"
        keywords = analyzer._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # 应该包含一些情感词
        assert any(kw in text for kw in keywords)
    
    def test_extract_keywords_chinese(self):
        """测试中文关键词提取"""
        analyzer = MoodAnalyzer()
        
        text = "这个Python程序运行得很好，我非常满意。"
        keywords = analyzer._extract_keywords(text)
        
        assert len(keywords) > 0
    
    def test_detect_topic(self):
        """测试主题检测"""
        analyzer = MoodAnalyzer()
        
        # 测试天气主题
        text = "今天天气很好，阳光明媚，适合出门。"
        topic = analyzer._detect_topic(text)
        
        assert topic is not None
        assert "天气" in topic or "sun" in topic.lower()
        
        # 测试编程主题
        text = "我喜欢用Python编程，代码运行很顺利。"
        topic = analyzer._detect_topic(text)
        
        assert "编程" in topic or "code" in topic.lower()
    
    def test_mood_result_str(self):
        """测试心情结果字符串表示"""
        result = MoodResult(
            mood_type=MoodType.HAPPY,
            confidence=0.85,
            reason="检测到积极词汇"
        )
        
        result_str = str(result)
        
        assert "HAPPY" in result_str
        assert "85%" in result_str
        assert "积极词汇" in result_str
    
    def test_mood_result_dict(self):
        """测试心情结果字典表示"""
        result = MoodResult(
            mood_type=MoodType.SAD,
            confidence=0.75,
            reason="检测到消极词汇"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["mood_type"] == "sad"
        assert result_dict["confidence"] == 0.75
        assert result_dict["reason"] == "检测到消极词汇"


class TestMoodManager:
    """心情管理器测试"""
    
    def test_initialization(self, mock_memory_storage):
        """测试初始化"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        assert manager.storage_manager == mock_memory_storage
        assert manager.current_mood == MoodType.NEUTRAL
        assert manager.mood_history == []
    
    def test_initialization_without_storage(self):
        """测试无存储初始化"""
        manager = MoodManager()
        
        assert manager.storage_manager is None
        assert manager.current_mood == MoodType.NEUTRAL
    
    def test_update_mood(self, mock_memory_storage):
        """测试更新心情"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        # 模拟分析结果
        test_result = MoodResult(
            mood_type=MoodType.HAPPY,
            confidence=0.8,
            reason="测试原因"
        )
        
        # 注册回调
        callback_called = []
        def test_callback(old_mood, new_result):
            callback_called.append((old_mood, new_result))
        
        manager.register_mood_change_callback(test_callback)
        
        # 更新心情
        result = manager.update_mood(test_result)
        
        assert result is True
        assert manager.current_mood == MoodType.HAPPY
        assert len(manager.mood_history) == 1
        
        # 回调应该被调用
        assert len(callback_called) == 1
        assert callback_called[0][0] == MoodType.NEUTRAL
        assert callback_called[0][1] == test_result
    
    def test_update_mood_same_mood(self, mock_memory_storage):
        """测试更新为相同心情"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        manager.current_mood = MoodType.HAPPY
        
        # 模拟相同心情的结果
        test_result = MoodResult(
            mood_type=MoodType.HAPPY,
            confidence=0.9,
            reason="相同心情"
        )
        
        # 注册回调
        callback_called = []
        def test_callback(old_mood, new_result):
            callback_called.append((old_mood, new_result))
        
        manager.register_mood_change_callback(test_callback)
        
        # 更新心情（应该不触发回调）
        result = manager.update_mood(test_result)
        
        assert result is True
        # 心情没变，但历史记录会增加
        assert len(manager.mood_history) == 1
        # 回调不应该被调用（心情没变化）
        assert len(callback_called) == 0
    
    def test_analyze_and_update(self, mock_memory_storage):
        """测试分析并更新"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        # 模拟分析器
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = MoodResult(
            mood_type=MoodType.SAD,
            confidence=0.7,
            reason="模拟分析"
        )
        
        manager.analyzer = mock_analyzer
        
        # 分析文本
        result = manager.analyze_and_update("我今天很难过")
        
        assert result is True
        assert manager.current_mood == MoodType.SAD
        mock_analyzer.analyze.assert_called_once_with("我今天很难过")
    
    def test_save_current_mood(self, mock_memory_storage):
        """测试保存当前心情"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        manager.current_mood = MoodType.HAPPY
        manager.mood_history = [MoodResult(
            mood_type=MoodType.HAPPY,
            confidence=0.8,
            reason="测试"
        )]
        
        result = manager.save_current_mood()
        
        assert result is True
        mock_memory_storage.save_mood.assert_called_once()
    
    def test_save_current_mood_no_storage(self):
        """测试无存储时保存心情"""
        manager = MoodManager()  # 无存储
        
        result = manager.save_current_mood()
        
        assert result is False
    
    def test_load_mood_history(self, mock_memory_storage):
        """测试加载心情历史"""
        # 模拟存储返回历史
        mock_history = [
            {"mood": "happy", "confidence": 0.8, "reason": "原因1"},
            {"mood": "sad", "confidence": 0.6, "reason": "原因2"}
        ]
        mock_memory_storage.load_mood_history.return_value = mock_history
        
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        history = manager.load_mood_history(limit=5)
        
        assert len(history) == 2
        assert all(isinstance(item, dict) for item in history)
        mock_memory_storage.load_mood_history.assert_called_once_with(5)
    
    def test_get_mood_stats(self, mock_memory_storage):
        """测试获取心情统计"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        # 添加一些历史记录
        manager.mood_history = [
            MoodResult(mood_type=MoodType.HAPPY, confidence=0.8, reason="1"),
            MoodResult(mood_type=MoodType.HAPPY, confidence=0.9, reason="2"),
            MoodResult(mood_type=MoodType.SAD, confidence=0.7, reason="3"),
            MoodResult(mood_type=MoodType.NEUTRAL, confidence=1.0, reason="4")
        ]
        
        stats = manager.get_mood_stats()
        
        assert "total" in stats
        assert "happy" in stats
        assert "sad" in stats
        assert "neutral" in stats
        assert stats["total"] == 4
        assert stats["happy"] == 2
        assert stats["sad"] == 1
        assert stats["neutral"] == 1
    
    def test_register_callback(self, mock_memory_storage):
        """测试注册回调"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        def callback1(old_mood, new_result):
            pass
        
        def callback2(old_mood, new_result):
            pass
        
        manager.register_mood_change_callback(callback1)
        manager.register_mood_change_callback(callback2)
        
        assert len(manager.mood_change_callbacks) == 2
    
    def test_unregister_callback(self, mock_memory_storage):
        """测试取消注册回调"""
        manager = MoodManager(storage_manager=mock_memory_storage)
        
        def callback1(old_mood, new_result):
            pass
        
        def callback2(old_mood, new_result):
            pass
        
        manager.register_mood_change_callback(callback1)
        manager.register_mood_change_callback(callback2)
        
        manager.unregister_mood_change_callback(callback1)
        
        assert len(manager.mood_change_callbacks) == 1
        assert callback2 in manager.mood_change_callbacks


class TestMoodImageManager:
    """心情图片管理器测试"""
    
    def test_initialization(self, temp_dir):
        """测试初始化"""
        # 创建临时资源目录
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建一些测试图片文件
        for mood in ["happy", "sad", "neutral", "angry"]:
            (moods_dir / f"{mood}.png").write_bytes(b"fake image data")
        
        manager = MoodImageManager(str(assets_dir))
        
        assert manager.assets_dir == str(assets_dir)
        assert manager.moods_dir == str(moods_dir)
    
    def test_get_mood_image_path(self, temp_dir):
        """测试获取心情图片路径"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建测试图片
        (moods_dir / "happy.png").write_bytes(b"fake image")
        (moods_dir / "sad.png").write_bytes(b"fake image")
        
        manager = MoodImageManager(str(assets_dir))
        
        # 测试存在的图片
        happy_path = manager.get_mood_image_path("happy")
        assert happy_path is not None
        assert "happy.png" in str(happy_path)
        
        # 测试不存在的图片（应该返回默认）
        unknown_path = manager.get_mood_image_path("unknown")
        assert unknown_path is not None
    
    def test_get_mood_image_path_default(self, temp_dir):
        """测试获取默认图片"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 只创建默认图片
        (moods_dir / "neutral.png").write_bytes(b"default image")
        
        manager = MoodImageManager(str(assets_dir))
        
        # 测试不存在的mood，应该返回默认
        path = manager.get_mood_image_path("nonexistent")
        assert path is not None
        assert "neutral.png" in str(path)
    
    def test_get_mood_image_path_no_default(self, temp_dir):
        """测试无默认图片的情况"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 不创建任何图片
        manager = MoodImageManager(str(assets_dir))
        
        # 应该返回None
        path = manager.get_mood_image_path("happy")
        assert path is None
    
    def test_get_all_mood_images(self, temp_dir):
        """测试获取所有心情图片"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建多个图片
        test_images = {
            "happy": "happy.png",
            "sad": "sad.png",
            "neutral": "neutral.png",
            "angry": "angry.png"
        }
        
        for filename in test_images.values():
            (moods_dir / filename).write_bytes(b"fake image")
        
        manager = MoodImageManager(str(assets_dir))
        
        images = manager.get_all_mood_images()
        
        assert len(images) == len(test_images)
        for mood, path in images.items():
            assert mood in test_images
            assert test_images[mood] in str(path)
    
    def test_load_image_data(self, temp_dir):
        """测试加载图片数据"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建测试图片文件
        test_data = b"PNG fake image data"
        (moods_dir / "test.png").write_bytes(test_data)
        
        manager = MoodImageManager(str(assets_dir))
        
        data = manager.load_image_data("test.png")
        
        assert data == test_data
    
    def test_load_image_data_nonexistent(self, temp_dir):
        """测试加载不存在的图片数据"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        manager = MoodImageManager(str(assets_dir))
        
        data = manager.load_image_data("nonexistent.png")
        
        assert data is None
    
    def test_check_images_exist(self, temp_dir):
        """测试检查图片是否存在"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建部分图片
        (moods_dir / "happy.png").write_bytes(b"data")
        (moods_dir / "sad.png").write_bytes(b"data")
        # 不创建neutral和angry
        
        manager = MoodImageManager(str(assets_dir))
        
        # 检查现有图片
        assert manager.check_image_exists("happy") is True
        assert manager.check_image_exists("sad") is True
        # 检查不存在的图片
        assert manager.check_image_exists("neutral") is False
        assert manager.check_image_exists("angry") is False
        assert manager.check_image_exists("nonexistent") is False
    
    def test_create_default_images(self, temp_dir):
        """测试创建默认图片"""
        assets_dir = temp_dir / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        manager = MoodImageManager(str(assets_dir))
        
        # 创建默认图片
        created = manager.create_default_images()
        
        # 应该创建了一些图片
        assert created > 0
        
        # 检查文件是否创建
        for mood in ["happy", "sad", "neutral", "angry"]:
            file_path = Path(moods_dir) / f"{mood}.png"
            if file_path.exists():
                # 文件应该包含"Default"字样
                data = file_path.read_bytes()
                assert b"Default" in data