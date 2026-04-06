#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心情定制示例
展示如何定制和扩展心情系统
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mood.analyzer import MoodAnalyzer, MoodResult, MoodType
from src.core.mood.manager import MoodManager
from src.core.mood.images import MoodImageManager
from src.core.memory.storage import MemoryStorage
from src.utils.config import get_config_manager
from src.utils.logger import get_logger, info
from src.utils.helpers import Timer, safe_execute
from src.utils.error_handler import safe_call


def example_custom_mood_rules():
    """示例1: 自定义心情规则"""
    print("=" * 60)
    print("示例1: 自定义心情规则")
    print("=" * 60)
    
    # 1. 创建自定义心情规则
    custom_rules = {
        "moods": {
            # 原有心情类型
            "happy": {
                "keywords": ["开心", "高兴", "喜欢", "爱", "棒", "好", "优秀", "完美"],
                "weight": 1.0,
                "decay_rate": 0.9,  # 衰减率
                "emoji": "😊"
            },
            "sad": {
                "keywords": ["伤心", "难过", "悲伤", "哭", "不好", "讨厌", "失望", "痛苦"],
                "weight": 1.0,
                "decay_rate": 0.8,
                "emoji": "😢"
            },
            "neutral": {
                "keywords": [],
                "weight": 0.5,
                "decay_rate": 1.0,
                "emoji": "😐"
            },
            "angry": {
                "keywords": ["生气", "愤怒", "恼火", "发怒", "暴躁", "不满"],
                "weight": 1.2,  # 愤怒情绪权重更高
                "decay_rate": 0.7,  # 愤怒情绪衰减更快
                "emoji": "😠"
            },
            "scared": {
                "keywords": ["害怕", "恐惧", "担心", "紧张", "惊吓", "恐怖"],
                "weight": 1.1,
                "decay_rate": 0.6,
                "emoji": "😨"
            },
            "confused": {
                "keywords": ["困惑", "疑惑", "不解", "迷茫", "糊涂", "不明白"],
                "weight": 0.9,
                "decay_rate": 0.8,
                "emoji": "🤔"
            },
            
            # 新增自定义心情类型
            "excited": {
                "keywords": ["激动", "兴奋", "太棒了", "哇塞", "惊喜", "刺激", "期待"],
                "weight": 1.3,  # 兴奋情绪权重高
                "decay_rate": 0.5,  # 兴奋情绪衰减慢
                "emoji": "🎉"
            },
            "calm": {
                "keywords": ["平静", "安宁", "放松", "舒缓", "宁静", "平和", "淡定"],
                "weight": 0.8,
                "decay_rate": 0.9,
                "emoji": "🧘"
            },
            "proud": {
                "keywords": ["自豪", "骄傲", "成就", "成功", "胜利", "优秀", "出色"],
                "weight": 1.1,
                "decay_rate": 0.8,
                "emoji": "🥇"
            },
            "lonely": {
                "keywords": ["孤独", "寂寞", "孤单", "独自", "无人", "空虚"],
                "weight": 1.0,
                "decay_rate": 0.7,
                "emoji": "🌌"
            },
            "playful": {
                "keywords": ["调皮", "玩笑", "搞笑", "幽默", "有趣", "好玩", "娱乐"],
                "weight": 0.9,
                "decay_rate": 0.6,
                "emoji": "🤪"
            }
        },
        "default_mood": "neutral",
        "rules": {
            "keyword_weight": 1.0,
            "context_weight": 0.3,
            "history_weight": 0.2,
            "decay_enabled": True,
            "decay_rate": 0.95
        }
    }
    
    # 2. 保存自定义规则
    config_manager = get_config_manager()
    result = config_manager.save_config("custom_mood_rules.json", custom_rules)
    
    if result:
        print("✅ 自定义心情规则已保存")
        
        # 显示统计信息
        moods = custom_rules["moods"]
        print(f"   心情类型数量: {len(moods)}")
        print(f"   基础心情: {list(moods.keys())[:6]}")
        print(f"   自定义心情: {list(moods.keys())[6:]}")
    else:
        print("❌ 保存规则失败")
    
    return custom_rules


def example_custom_mood_type():
    """示例2: 创建自定义心情类型"""
    print("\n" + "=" * 60)
    print("示例2: 创建自定义心情类型")
    print("=" * 60)
    
    # 1. 扩展MoodType枚举
    from enum import Enum
    
    class ExtendedMoodType(Enum):
        """扩展的心情类型枚举"""
        # 基础心情
        HAPPY = "happy"
        SAD = "sad"
        NEUTRAL = "neutral"
        ANGRY = "angry"
        SCARED = "scared"
        CONFUSED = "confused"
        
        # 扩展心情
        EXCITED = "excited"
        CALM = "calm"
        PROUD = "proud"
        LONELY = "lonely"
        PLAYFUL = "playful"
        ROMANTIC = "romantic"
        NOSTALGIC = "nostalgic"
        INSPIRED = "inspired"
        GRATEFUL = "grateful"
        DETERMINED = "determined"
    
    # 2. 为自定义心情类型添加显示信息
    mood_display_info = {
        ExtendedMoodType.ROMANTIC: {
            "display_name": "浪漫",
            "emoji": "💕",
            "description": "感到浪漫和温馨",
            "color": "#FF69B4"  # 粉红色
        },
        ExtendedMoodType.NOSTALGIC: {
            "display_name": "怀旧",
            "emoji": "📻",
            "description": "怀念过去的美好时光",
            "color": "#8B4513"  # 棕色
        },
        ExtendedMoodType.INSPIRED: {
            "display_name": "鼓舞",
            "emoji": "✨",
            "description": "受到启发和鼓舞",
            "color": "#00CED1"  # 青色
        },
        ExtendedMoodType.GRATEFUL: {
            "display_name": "感恩",
            "emoji": "🙏",
            "description": "心怀感激和感谢",
            "color": "#32CD32"  # 绿色
        },
        ExtendedMoodType.DETERMINED: {
            "display_name": "决心",
            "emoji": "💪",
            "description": "充满决心和毅力",
            "color": "#FF4500"  # 橙红色
        }
    }
    
    # 3. 演示自定义心情类型
    print("🎭 自定义心情类型:")
    for mood_type, info in mood_display_info.items():
        print(f"\n   {info['emoji']} {info['display_name']} ({mood_type.value})")
        print(f"      描述: {info['description']}")
        print(f"      颜色: {info['color']}")
    
    return ExtendedMoodType, mood_display_info


def example_custom_analyzer():
    """示例3: 自定义心情分析器"""
    print("\n" + "=" * 60)
    print("示例3: 自定义心情分析器")
    print("=" * 60)
    
    # 1. 创建自定义心情分析器
    class CustomMoodAnalyzer(MoodAnalyzer):
        """自定义心情分析器，添加额外功能"""
        
        def __init__(self, rules_file: str = None, use_advanced: bool = False):
            super().__init__(rules_file)
            self.use_advanced = use_advanced
            self.analysis_history = []
            
            # 添加自定义关键词
            self.custom_keywords = {
                "programming": ["代码", "编程", "Python", "算法", "调试", "bug"],
                "learning": ["学习", "教程", "课程", "知识", "掌握", "理解"],
                "creative": ["创作", "艺术", "设计", "创意", "灵感", "想象"]
            }
            
            print("🔧 自定义心情分析器已初始化")
            if use_advanced:
                print("   启用高级分析模式")
        
        def analyze_with_context(self, text: str, context: Dict[str, Any] = None) -> MoodResult:
            """带上下文的心情分析"""
            context = context or {}
            
            # 基础分析
            base_result = self.analyze(text)
            
            # 上下文影响
            if context:
                context_factor = self._calculate_context_factor(context)
                # 根据上下文调整置信度
                base_result.confidence *= context_factor
            
            # 记录分析历史
            self.analysis_history.append({
                "text": text[:100],  # 只保存前100字符
                "result": base_result.to_dict(),
                "context": context,
                "timestamp": "2024-01-01T00:00:00"  # 实际使用中应使用当前时间
            })
            
            # 限制历史记录大小
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]
            
            return base_result
        
        def _calculate_context_factor(self, context: Dict[str, Any]) -> float:
            """计算上下文影响因子"""
            factor = 1.0
            
            # 时间因素（如夜晚可能更感性）
            hour = context.get("hour", 12)
            if 22 <= hour < 6:  # 夜晚
                factor *= 1.1
            
            # 对话历史因素
            history_count = context.get("conversation_count", 0)
            if history_count > 10:
                factor *= 0.9  # 长时间对话可能疲劳
            
            # 用户情绪状态
            user_mood = context.get("user_mood")
            if user_mood in ["happy", "excited"]:
                factor *= 1.05
            
            return factor
        
        def get_analysis_stats(self) -> Dict[str, Any]:
            """获取分析统计"""
            if not self.analysis_history:
                return {}
            
            mood_counts = {}
            total_confidence = 0
            
            for record in self.analysis_history:
                result = record["result"]
                mood = result.get("mood_type")
                confidence = result.get("confidence", 0)
                
                if mood:
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
                    total_confidence += confidence
            
            avg_confidence = total_confidence / len(self.analysis_history) if self.analysis_history else 0
            
            return {
                "total_analyses": len(self.analysis_history),
                "mood_distribution": mood_counts,
                "avg_confidence": avg_confidence,
                "unique_moods": len(mood_counts)
            }
    
    # 2. 测试自定义分析器
    print("🔍 测试自定义分析器...")
    
    analyzer = CustomMoodAnalyzer(use_advanced=True)
    
    # 测试文本
    test_texts = [
        "我今天完成了项目，感觉很兴奋！",
        "学习新知识让我感到很充实",
        "深夜写代码，有点孤独但也很专注"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n  测试 {i}: '{text}'")
        
        # 添加上下文
        context = {
            "hour": 23 if i == 3 else 14,  # 模拟时间
            "conversation_count": i * 5,
            "user_mood": "happy" if i == 1 else "neutral"
        }
        
        with Timer("带上下文分析"):
            result = analyzer.analyze_with_context(text, context)
        
        print(f"     心情: {result.mood_type.value}")
        print(f"     置信度: {result.confidence:.1%}")
        print(f"     原因: {result.reason[:50]}...")
    
    # 3. 获取统计
    stats = analyzer.get_analysis_stats()
    print(f"\n📊 分析统计:")
    print(f"   总分析次数: {stats.get('total_analyses', 0)}")
    print(f"   唯一心情数: {stats.get('unique_moods', 0)}")
    print(f"   平均置信度: {stats.get('avg_confidence', 0):.1%}")
    
    return analyzer


def example_custom_mood_manager():
    """示例4: 自定义心情管理器"""
    print("\n" + "=" * 60)
    print("示例4: 自定义心情管理器")
    print("=" * 60)
    
    # 1. 创建自定义心情管理器
    class CustomMoodManager(MoodManager):
        """自定义心情管理器，添加额外功能"""
        
        def __init__(self, storage_manager=None, enable_persistence=True):
            super().__init__(storage_manager)
            self.enable_persistence = enable_persistence
            self.mood_trends = []
            self.custom_callbacks = []
            
            print("🔧 自定义心情管理器已初始化")
            if enable_persistence:
                print("   启用持久化功能")
        
        def analyze_and_update_with_metadata(self, text: str, metadata: Dict[str, Any] = None) -> bool:
            """带元数据的心情分析"""
            metadata = metadata or {}
            
            # 调用基础分析
            result = super().analyze_and_update(text)
            
            if result and self.enable_persistence:
                # 保存元数据
                self._save_mood_metadata(metadata)
                
                # 记录趋势
                self._record_mood_trend(metadata)
            
            return result
        
        def _save_mood_metadata(self, metadata: Dict[str, Any]):
            """保存心情元数据"""
            # 在实际应用中，这里可以将元数据保存到数据库
            metadata_to_save = {
                "timestamp": "2024-01-01T00:00:00",
                "current_mood": self.current_mood.value,
                "metadata": metadata
            }
            
            # 模拟保存
            if self.storage_manager:
                # 这里可以调用存储管理器保存元数据
                pass
        
        def _record_mood_trend(self, metadata: Dict[str, Any]):
            """记录心情趋势"""
            trend_entry = {
                "mood": self.current_mood.value,
                "confidence": metadata.get("confidence", 0.5),
                "source": metadata.get("source", "unknown"),
                "timestamp": metadata.get("timestamp", "2024-01-01T00:00:00")
            }
            
            self.mood_trends.append(trend_entry)
            
            # 限制趋势记录大小
            if len(self.mood_trends) > 1000:
                self.mood_trends = self.mood_trends[-1000:]
        
        def get_mood_trends(self, window_size: int = 10) -> List[Dict[str, Any]]:
            """获取心情趋势"""
            if not self.mood_trends:
                return []
            
            # 返回最近的趋势
            return self.mood_trends[-window_size:]
        
        def get_mood_summary(self) -> Dict[str, Any]:
            """获取心情摘要"""
            if not self.mood_history:
                return {"message": "无心情历史"}
            
            # 计算各种统计
            total = len(self.mood_history)
            mood_counts = {}
            total_confidence = 0
            
            for record in self.mood_history:
                mood = record.mood_type.value
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
                total_confidence += record.confidence
            
            avg_confidence = total_confidence / total if total > 0 else 0
            
            # 找出主要心情
            main_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else "unknown"
            
            return {
                "total_records": total,
                "main_mood": main_mood,
                "mood_distribution": mood_counts,
                "avg_confidence": avg_confidence,
                "current_mood": self.current_mood.value,
                "trend_count": len(self.mood_trends)
            }
        
        def register_custom_callback(self, callback_type: str, callback: callable):
            """注册自定义回调"""
            self.custom_callbacks.append({
                "type": callback_type,
                "callback": callback
            })
            print(f"✅ 注册自定义回调: {callback_type}")
    
    # 2. 测试自定义管理器
    print("🔍 测试自定义心情管理器...")
    
    # 创建存储管理器（模拟）
    storage_manager = MemoryStorage()
    
    # 创建自定义管理器
    manager = CustomMoodManager(
        storage_manager=storage_manager,
        enable_persistence=True
    )
    
    # 注册心情变化回调
    def on_mood_change(old_mood, new_result):
        print(f"🎭 心情变化: {old_mood.value} -> {new_result.mood_type.value}")
    
    manager.register_mood_change_callback(on_mood_change)
    
    # 测试多次心情更新
    test_cases = [
        {
            "text": "项目完成了，太开心了！",
            "metadata": {"source": "project", "importance": "high"}
        },
        {
            "text": "代码有bug，有点烦躁",
            "metadata": {"source": "coding", "frustration_level": "medium"}
        },
        {
            "text": "学习新框架很有收获",
            "metadata": {"source": "learning", "satisfaction": "high"}
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  测试 {i}: {test['text']}")
        manager.analyze_and_update_with_metadata(test["text"], test["metadata"])
    
    # 3. 获取摘要
    summary = manager.get_mood_summary()
    print(f"\n📊 心情摘要:")
    print(f"   总记录数: {summary['total_records']}")
    print(f"   当前心情: {summary['current_mood']}")
    print(f"   主要心情: {summary['main_mood']}")
    print(f"   平均置信度: {summary['avg_confidence']:.1%}")
    
    # 4. 获取趋势
    trends = manager.get_mood_trends(window_size=3)
    print(f"\n📈 最近心情趋势 ({len(trends)} 条):")
    for trend in trends:
        print(f"   - {trend['mood']} (来源: {trend.get('source', 'unknown')})")
    
    return manager


def example_custom_mood_images():
    """示例5: 自定义心情图片"""
    print("\n" + "=" * 60)
    print("示例5: 自定义心情图片")
    print("=" * 60)
    
    # 1. 创建自定义心情图片管理器
    class CustomMoodImageManager(MoodImageManager):
        """自定义心情图片管理器"""
        
        def __init__(self, assets_dir: str = None, enable_cache: bool = True):
            super().__init__(assets_dir)
            self.enable_cache = enable_cache
            self.image_cache = {}
            self.custom_moods = {}
            
            print("🔧 自定义图片管理器已初始化")
            if enable_cache:
                print("   启用图片缓存")
        
        def register_custom_mood(self, mood_type: str, image_path: str, metadata: Dict[str, Any] = None):
            """注册自定义心情类型"""
            self.custom_moods[mood_type] = {
                "image_path": image_path,
                "metadata": metadata or {},
                "registered_at": "2024-01-01T00:00:00"
            }
            print(f"✅ 注册自定义心情: {mood_type} -> {image_path}")
        
        def get_mood_image_path(self, mood_type: str) -> Optional[Path]:
            """获取心情图片路径（支持自定义心情）"""
            # 首先检查自定义心情
            if mood_type in self.custom_moods:
                custom_info = self.custom_moods[mood_type]
                custom_path = Path(custom_info["image_path"])
                
                if custom_path.exists():
                    return custom_path
                else:
                    print(f"⚠️  自定义心情图片不存在: {custom_path}")
            
            # 回退到默认实现
            return super().get_mood_image_path(mood_type)
        
        def get_all_mood_images(self, include_custom: bool = True) -> Dict[str, Path]:
            """获取所有心情图片"""
            images = super().get_all_mood_images()
            
            if include_custom and self.custom_moods:
                for mood_type, info in self.custom_moods.items():
                    image_path = Path(info["image_path"])
                    if image_path.exists():
                        images[mood_type] = image_path
            
            return images
        
        def generate_mood_preview(self, mood_type: str, size: tuple = (100, 100)) -> Dict[str, Any]:
            """生成心情预览信息"""
            image_path = self.get_mood_image_path(mood_type)
            
            preview = {
                "mood_type": mood_type,
                "has_image": image_path is not None and image_path.exists(),
                "image_size": size,
                "is_custom": mood_type in self.custom_moods
            }
            
            if preview["is_custom"]:
                preview.update(self.custom_moods[mood_type]["metadata"])
            
            return preview
        
        def clear_cache(self):
            """清空图片缓存"""
            self.image_cache.clear()
            print("🧹 图片缓存已清空")
    
    # 2. 测试自定义图片管理器
    print("🔍 测试自定义图片管理器...")
    
    # 创建临时测试目录
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建assets目录结构
        assets_dir = Path(temp_dir) / "assets"
        moods_dir = assets_dir / "moods"
        moods_dir.mkdir(parents=True)
        
        # 创建一些测试图片文件
        for mood in ["happy", "sad", "neutral", "excited", "calm"]:
            image_file = moods_dir / f"{mood}.png"
            # 创建模拟图片文件
            image_file.write_bytes(b"fake image data")
        
        # 创建自定义管理器
        manager = CustomMoodImageManager(str(assets_dir), enable_cache=True)
        
        # 注册自定义心情
        custom_image_path = moods_dir / "custom_mood.png"
        custom_image_path.write_bytes(b"custom image data")
        
        manager.register_custom_mood(
            mood_type="magical",
            image_path=str(custom_image_path),
            metadata={
                "description": "魔法般的心情",
                "color": "#9B30FF",
                "intensity": "high"
            }
        )
        
        # 测试获取图片路径
        test_moods = ["happy", "sad", "magical", "unknown"]
        
        for mood in test_moods:
            print(f"\n🔍 获取心情图片: {mood}")
            path = manager.get_mood_image_path(mood)
            
            if path and path.exists():
                print(f"✅ 图片路径: {path.name}")
                if mood == "magical":
                    print("✨ 这是自定义心情!")
            else:
                print(f"❌ 未找到图片")
        
        # 获取所有图片
        all_images = manager.get_all_mood_images(include_custom=True)
        print(f"\n📁 所有心情图片: {len(all_images)} 个")
        for mood, path in all_images.items():
            print(f"   - {mood}: {path.name}")
        
        # 生成预览
        print(f"\n🖼️ 心情预览:")
        for mood in ["happy", "magical"]:
            preview = manager.generate_mood_preview(mood, size=(150, 150))
            print(f"\n   {mood}:")
            for key, value in preview.items():
                print(f"     {key}: {value}")
    
    return manager


def example_mood_integration():
    """示例6: 心情系统集成示例"""
    print("\n" + "=" * 60)
    print("示例6: 心情系统集成示例")
    print("=" * 60)
    
    # 1. 创建完整的自定义心情系统
    print("🔧 创建完整的心情系统...")
    
    # 创建存储
    storage = MemoryStorage()
    
    # 创建自定义分析器
    analyzer = CustomMoodAnalyzer(use_advanced=True)
    
    # 创建自定义管理器
    manager = CustomMoodManager(
        storage_manager=storage,
        enable_persistence=True
    )
    
    # 替换默认分析器
    manager.analyzer = analyzer
    
    # 2. 模拟对话流程
    print("\n💬 模拟对话流程:")
    
    conversation = [
        "今天天气真好，心情特别愉快！",
        "工作遇到了困难，有点沮丧...",
        "但是解决了问题，感觉很自豪！",
        "晚上放松一下，看看电影"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n   回合 {i}:")
        print(f"   用户: {message}")
        
        # 分析心情
        with Timer("心情分析"):
            result = manager.analyze_and_update_with_metadata(
                message,
                metadata={
                    "round": i,
                    "message_length": len(message),
                    "timestamp": f"2024-01-01T{i:02d}:00:00"
                }
            )
        
        if result:
            current_mood = manager.current_mood
            print(f"   🎭 AI心情: {current_mood.value}")
            
            # 获取简要分析
            if hasattr(analyzer, 'get_analysis_stats'):
                stats = analyzer.get_analysis_stats()
                if stats:
                    print(f"   📊 分析统计: {stats.get('total_analyses', 0)} 次")
    
    # 3. 获取完整报告
    print("\n📈 心情系统报告:")
    
    # 从管理器获取摘要
    summary = manager.get_mood_summary()
    print(f"\n   心情摘要:")
    print(f"     总分析次数: {summary.get('total_records', 0)}")
    print(f"     当前心情: {summary.get('current_mood')}")
    print(f"     主要心情: {summary.get('main_mood')}")
    
    # 从分析器获取统计
    if hasattr(analyzer, 'get_analysis_stats'):
        stats = analyzer.get_analysis_stats()
        if stats:
            print(f"\n   分析统计:")
            print(f"     唯一心情数: {stats.get('unique_moods', 0)}")
            print(f"     平均置信度: {stats.get('avg_confidence', 0):.1%}")
            
            # 显示心情分布
            distribution = stats.get('mood_distribution', {})
            if distribution:
                print(f"\n   心情分布:")
                for mood, count in distribution.items():
                    percentage = count / stats['total_analyses'] * 100
                    print(f"     {mood}: {count} 次 ({percentage:.1f}%)")
    
    # 4. 保存心情记录
    print(f"\n💾 保存心情记录...")
    save_result = manager.save_current_mood()
    if save_result:
        print("✅ 心情记录已保存")
    else:
        print("❌ 保存心情记录失败")
    
    return manager, analyzer


@safe_call(operation="心情定制示例")
def main():
    """主函数 - 运行所有示例"""
    print("🚀 AI宠物MVP - 心情定制示例")
    print("=" * 60)
    print("本示例演示如何定制和扩展心情系统")
    print("=" * 60)
    
    # 记录开始时间
    from src.utils.helpers import Timer
    total_timer = Timer("完整示例运行")
    
    try:
        # 运行各个示例
        example_custom_mood_rules()
        example_custom_mood_type()
        example_custom_analyzer()
        example_custom_mood_manager()
        example_custom_mood_images()
        example_mood_integration()
        
        print("\n" + "=" * 60)
        print("🎉 心情定制示例完成！")
        print("=" * 60)
        
        # 总结
        print("\n📋 关键定制功能总结:")
        print("1. ✅ 自定义心情规则 - 添加新的心情类型和规则")
        print("2. ✅ 自定义心情类型 - 扩展MoodType枚举")
        print("3. ✅ 自定义分析器 - 添加上下文分析和统计")
        print("4. ✅ 自定义管理器 - 添加元数据和趋势跟踪")
        print("5. ✅ 自定义图片 - 支持自定义心情图片")
        print("6. ✅ 系统集成 - 完整的心情系统集成")
        
        print("\n🔧 实际应用建议:")
        print("1. 在 data/config/ 中创建自定义心情规则")
        print("2. 根据需要扩展MoodType枚举")
        print("3. 为特殊场景创建专用分析器")
        print("4. 使用元数据记录额外信息")
        print("5. 为自定义心情创建图片资源")
        
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n\n示例运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止计时
        total_timer.stop()
        print(f"\n⏱️  总运行时间: {total_timer.format_result()}")
        print("=" * 60)


if __name__ == "__main__":
    main()
    print("\n👋 示例程序结束")