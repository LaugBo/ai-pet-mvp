# 心情管理器
# 功能：管理AI宠物的心情状态，包括心情切换、持久化和状态跟踪

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from .analyzer import MoodType, MoodResult, MoodAnalyzer

class MoodState(Enum):
    """心情状态"""
    ACTIVE = "active"      # 活跃状态
    FADING = "fading"      # 淡出状态
    TRANSITION = "transition"  # 切换状态

@dataclass
class MoodEntry:
    """心情记录条目"""
    mood_type: MoodType       # 心情类型
    confidence: float         # 置信度
    timestamp: float         # 时间戳
    duration: float          # 持续时间（秒）
    triggers: List[str]      # 触发词
    reason: str              # 原因
    conversation_id: Optional[str] = None  # 关联对话ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "mood": self.mood_type.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "triggers": self.triggers,
            "reason": self.reason,
            "conversation_id": self.conversation_id
        }

class MoodManager:
    """
    心情管理器
    管理AI宠物的心情状态
    """
    
    def __init__(self, config_path: str = None, storage_manager=None):
        """
        初始化心情管理器
        
        参数:
            config_path: 配置文件路径
            storage_manager: 存储管理器实例
        """
        # 初始化分析器
        self.analyzer = MoodAnalyzer(config_path)
        
        # 当前心情状态
        self.current_mood = MoodType.NEUTRAL
        self.current_confidence = 0.0
        self.current_triggers = []
        self.current_reason = "初始状态"
        self.mood_start_time = time.time()
        self.mood_state = MoodState.ACTIVE
        
        # 心情历史
        self.mood_history: List[MoodEntry] = []
        self.max_history_size = 1000
        
        # 存储管理器
        self.storage_manager = storage_manager
        
        # 心情配置
        self.mood_config = {
            "default_duration": 60.0,  # 默认心情持续时间（秒）
            "min_confidence": 0.3,     # 最小置信度
            "persistence_factor": 0.7,  # 心情保持因子
            "smooth_transition": True,  # 是否平滑过渡
            "auto_save": True,         # 是否自动保存
            "save_interval": 300       # 保存间隔（秒）
        }
        
        # 回调函数
        self.on_mood_change_callbacks = []
        
        # 加载配置
        if config_path:
            self._load_config(config_path)
        
        print(f"心情管理器初始化完成")
        print(f"当前心情: {self.current_mood.value}")
        print(f"历史记录容量: {self.max_history_size}")
    
    def _load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "mood_config" in config:
                self.mood_config.update(config["mood_config"])
            
            print(f"✅ 从配置文件加载心情配置: {config_path}")
            
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在: {config_path}, 使用默认配置")
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
    
    def analyze_and_update_mood(self, text: str, conversation_id: str = None) -> MoodResult:
        """
        分析文本并更新心情
        
        参数:
            text: 要分析的文本
            conversation_id: 对话ID（可选）
            
        返回:
            心情分析结果
        """
        # 分析文本
        result = self.analyzer.analyze_text(text)
        
        # 检查是否需要更新心情
        should_update = self._should_update_mood(result)
        
        if should_update:
            self._update_mood(result, conversation_id)
        
        return result
    
    def _should_update_mood(self, new_result: MoodResult) -> bool:
        """检查是否需要更新心情"""
        # 置信度过低则不更新
        if new_result.confidence < self.mood_config["min_confidence"]:
            return False
        
        # 如果是中性心情，不更新
        if new_result.mood_type == MoodType.NEUTRAL:
            return False
        
        # 如果新心情和当前心情相同，检查置信度
        if new_result.mood_type == self.current_mood:
            # 新置信度明显更高时才更新
            return new_result.confidence > self.current_confidence * 1.2
        
        # 新心情置信度足够高时更新
        return new_result.confidence >= self.mood_config["min_confidence"]
    
    def _update_mood(self, new_result: MoodResult, conversation_id: str = None):
        """更新心情"""
        # 保存旧心情到历史
        old_duration = time.time() - self.mood_start_time
        if old_duration > 0:  # 避免初始状态
            old_entry = MoodEntry(
                mood_type=self.current_mood,
                confidence=self.current_confidence,
                timestamp=self.mood_start_time,
                duration=old_duration,
                triggers=self.current_triggers,
                reason=self.current_reason
            )
            self._add_to_history(old_entry)
        
        # 更新当前心情
        old_mood = self.current_mood
        self.current_mood = new_result.mood_type
        self.current_confidence = new_result.confidence
        self.current_triggers = new_result.triggers
        self.current_reason = new_result.reason
        self.mood_start_time = time.time()
        
        # 记录新心情
        new_entry = MoodEntry(
            mood_type=self.current_mood,
            confidence=self.current_confidence,
            timestamp=self.mood_start_time,
            duration=0.0,  # 刚刚开始
            triggers=self.current_triggers,
            reason=self.current_reason,
            conversation_id=conversation_id
        )
        self.mood_history.append(new_entry)
        
        # 触发回调
        self._trigger_mood_change_callbacks(old_mood, new_result)
        
        # 保存到存储
        if self.mood_config["auto_save"] and self.storage_manager:
            self._save_mood_record(new_entry)
        
        print(f"🎭 心情更新: {old_mood.value} -> {self.current_mood.value}")
        print(f"   原因: {self.current_reason}")
        print(f"   置信度: {self.current_confidence:.2%}")
    
    def _add_to_history(self, entry: MoodEntry):
        """添加到历史记录"""
        self.mood_history.append(entry)
        
        # 限制历史记录大小
        if len(self.mood_history) > self.max_history_size:
            self.mood_history = self.mood_history[-self.max_history_size:]
    
    def _trigger_mood_change_callbacks(self, old_mood: MoodType, new_result: MoodResult):
        """触发心情变化回调"""
        for callback in self.on_mood_change_callbacks:
            try:
                callback(old_mood, new_result)
            except Exception as e:
                print(f"❌ 心情变化回调执行失败: {e}")
    
    def _save_mood_record(self, entry: MoodEntry):
        """保存心情记录"""
        try:
            if self.storage_manager and hasattr(self.storage_manager, 'save_mood_record'):
                mood_data = entry.to_dict()
                mood_data["manager_version"] = "1.0"
                self.storage_manager.save_mood_record(mood_data)
        except Exception as e:
            print(f"❌ 保存心情记录失败: {e}")
    
    def register_mood_change_callback(self, callback: Callable):
        """
        注册心情变化回调
        
        参数:
            callback: 回调函数，接收(old_mood, new_result)两个参数
        """
        self.on_mood_change_callbacks.append(callback)
        print(f"✅ 注册心情变化回调，当前回调数: {len(self.on_mood_change_callbacks)}")
    
    def get_current_mood_info(self) -> Dict[str, Any]:
        """
        获取当前心情信息
        
        返回:
            当前心情信息
        """
        current_duration = time.time() - self.mood_start_time
        
        return {
            "mood": self.current_mood.value,
            "confidence": self.current_confidence,
            "duration": current_duration,
            "triggers": self.current_triggers,
            "reason": self.current_reason,
            "state": self.mood_state.value,
            "start_time": datetime.fromtimestamp(self.mood_start_time).isoformat()
        }
    
    def get_mood_history_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取心情历史摘要
        
        参数:
            hours: 统计小时数
            
        返回:
            心情摘要
        """
        cutoff_time = time.time() - (hours * 3600)
        
        # 过滤指定时间范围内的记录
        recent_history = [
            entry for entry in self.mood_history
            if entry.timestamp >= cutoff_time
        ]
        
        if not recent_history:
            return {
                "period_hours": hours,
                "total_records": 0,
                "most_common_mood": "neutral",
                "mood_distribution": {},
                "average_confidence": 0.0
            }
        
        # 使用分析器生成摘要
        mood_data = [entry.to_dict() for entry in recent_history]
        summary = self.analyzer.get_mood_history_summary(mood_data)
        summary["period_hours"] = hours
        summary["total_records"] = len(recent_history)
        
        return summary
    
    def get_recent_moods(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的心情记录
        
        参数:
            count: 记录数量
            
        返回:
            最近心情记录列表
        """
        recent = self.mood_history[-count:] if self.mood_history else []
        return [entry.to_dict() for entry in recent]
    
    def force_set_mood(self, mood_type: MoodType, reason: str = "手动设置"):
        """
        强制设置心情（用于特殊事件）
        
        参数:
            mood_type: 心情类型
            reason: 设置原因
        """
        result = MoodResult(
            mood_type=mood_type,
            confidence=1.0,
            triggers=["manual"],
            reason=reason
        )
        
        self._update_mood(result)
        print(f"🎭 强制设置心情: {mood_type.value} ({reason})")
    
    def get_mood_trend(self, window_size: int = 10) -> List[str]:
        """
        获取心情趋势
        
        参数:
            window_size: 窗口大小
            
        返回:
            心情趋势列表
        """
        if len(self.mood_history) < window_size:
            return []
        
        # 获取最近的心情记录
        recent_moods = self.mood_history[-window_size:]
        mood_types = [entry.mood_type.value for entry in recent_moods]
        
        return mood_types
    
    def clear_history(self):
        """清空心情历史"""
        self.mood_history.clear()
        print("🗑️ 心情历史已清空")
    
    def save_to_file(self, filepath: str):
        """
        保存心情数据到文件
        
        参数:
            filepath: 文件路径
        """
        try:
            data = {
                "current_mood": self.current_mood.value,
                "current_confidence": self.current_confidence,
                "current_triggers": self.current_triggers,
                "current_reason": self.current_reason,
                "mood_start_time": self.mood_start_time,
                "history": [entry.to_dict() for entry in self.mood_history],
                "config": self.mood_config
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 心情数据保存到: {filepath}")
            
        except Exception as e:
            print(f"❌ 保存心情数据失败: {e}")
    
    def load_from_file(self, filepath: str) -> bool:
        """
        从文件加载心情数据
        
        参数:
            filepath: 文件路径
            
        返回:
            是否加载成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复当前心情
            self.current_mood = MoodType(data["current_mood"])
            self.current_confidence = data["current_confidence"]
            self.current_triggers = data["current_triggers"]
            self.current_reason = data["current_reason"]
            self.mood_start_time = data["mood_start_time"]
            
            # 恢复历史
            self.mood_history = []
            for entry_data in data["history"]:
                entry = MoodEntry(
                    mood_type=MoodType(entry_data["mood"]),
                    confidence=entry_data["confidence"],
                    timestamp=entry_data["timestamp"],
                    duration=entry_data["duration"],
                    triggers=entry_data["triggers"],
                    reason=entry_data["reason"],
                    conversation_id=entry_data.get("conversation_id")
                )
                self.mood_history.append(entry)
            
            # 恢复配置
            if "config" in data:
                self.mood_config.update(data["config"])
            
            print(f"✅ 从文件加载心情数据: {filepath}")
            print(f"   恢复心情: {self.current_mood.value}")
            print(f"   历史记录: {len(self.mood_history)} 条")
            
            return True
            
        except FileNotFoundError:
            print(f"⚠️ 心情数据文件不存在: {filepath}")
            return False
        except Exception as e:
            print(f"❌ 加载心情数据失败: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    print("心情管理器测试")
    print("=" * 50)
    
    # 创建管理器
    manager = MoodManager()
    
    # 测试心情分析
    test_texts = [
        "我今天特别开心！",
        "为什么会这样？我不明白。",
        "有点难过，但我会加油的！"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n分析文本 {i}: {text}")
        result = manager.analyze_and_update_mood(text)
        print(f"  心情: {result.mood_type.value}")
        print(f"  置信度: {result.confidence:.2%}")
    
    # 获取当前心情信息
    print("\n" + "=" * 50)
    print("当前心情信息:")
    current_info = manager.get_current_mood_info()
    for key, value in current_info.items():
        print(f"  {key}: {value}")
    
    # 测试强制设置心情
    print("\n测试强制设置心情...")
    manager.force_set_mood(MoodType.HAPPY, "测试强制设置")
    
    # 获取心情摘要
    print("\n心情历史摘要:")
    summary = manager.get_mood_history_summary(hours=1)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("=" * 50)
    print("心情管理器测试完成")