# 心情分析器
# 功能：分析对话内容，判断AI的心情状态

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MoodType(Enum):
    """心情类型枚举"""
    HAPPY = "happy"      # 开心
    EXCITED = "excited"  # 兴奋
    SAD = "sad"          # 低落
    PROUD = "proud"      # 自豪
    CONFUSED = "confused"  # 困惑
    NEUTRAL = "neutral"  # 中性

@dataclass
class MoodResult:
    """心情分析结果"""
    mood_type: MoodType           # 心情类型
    confidence: float             # 置信度 (0.0-1.0)
    triggers: List[str]           # 触发关键词
    reason: str                   # 分析原因
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "mood": self.mood_type.value,
            "confidence": self.confidence,
            "triggers": self.triggers,
            "reason": self.reason
        }

class MoodAnalyzer:
    """
    心情分析器
    分析文本内容，判断情绪状态
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化心情分析器
        
        参数:
            config_path: 配置文件路径
        """
        # 默认关键词配置
        self.keyword_patterns = {
            MoodType.HAPPY: {
                "keywords": ["开心", "高兴", "快乐", "愉快", "欢乐", "哈哈", "呵呵", "嘻嘻", "太棒了", "棒极了", "爱你", "喜欢", "爱", "幸福", "满足"],
                "weight": 1.0
            },
            MoodType.EXCITED: {
                "keywords": ["兴奋", "激动", "惊喜", "惊喜", "震惊", "哇", "喔", "天啊", "太棒了", "厉害", "成功", "胜利", "赢", "冠军", "第一"],
                "weight": 1.0
            },
            MoodType.SAD: {
                "keywords": ["难过", "伤心", "悲伤", "哭", "泪", "唉", "唉声叹气", "失望", "失落", "痛苦", "孤独", "寂寞", "想念", "想家", "分手"],
                "weight": 1.0
            },
            MoodType.PROUD: {
                "keywords": ["自豪", "骄傲", "成就", "优秀", "成功", "完美", "厉害", "出色", "超棒", "天才", "冠军", "金牌", "荣誉", "获奖", "表扬"],
                "weight": 1.0
            },
            MoodType.CONFUSED: {
                "keywords": ["困惑", "疑惑", "不明白", "不懂", "为什么", "怎么", "如何", "什么", "哪里", "谁", "疑问", "问题", "不确定", "?", "？"],
                "weight": 1.0
            }
        }
        
        # 情感强度词
        self.intensity_words = {
            "非常": 1.5, "特别": 1.5, "极其": 1.5, "十分": 1.3, "很": 1.2,
            "有点": 0.8, "稍微": 0.8, "略": 0.8, "微": 0.8
        }
        
        # 否定词
        self.negative_words = ["不", "没", "无", "非", "未", "否", "别", "勿", "莫"]
        
        # 加载配置文件
        if config_path:
            self._load_config(config_path)
        
        # 编译正则表达式
        self._compile_patterns()
        
        print(f"心情分析器初始化完成")
        print(f"支持的心情类型: {[mood.value for mood in self.keyword_patterns.keys()]}")
    
    def _load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "moods" in config:
                for mood_name, mood_config in config["moods"].items():
                    try:
                        mood_type = MoodType(mood_name)
                        if "keywords" in mood_config:
                            self.keyword_patterns[mood_type]["keywords"] = mood_config["keywords"]
                    except ValueError:
                        print(f"⚠️ 未知心情类型: {mood_name}")
            
            print(f"✅ 从配置文件加载心情规则: {config_path}")
            
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在: {config_path}, 使用默认配置")
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.compiled_patterns = {}
        for mood_type, config in self.keyword_patterns.items():
            # 为每个关键词创建正则表达式
            patterns = []
            for keyword in config.get("keywords", []):
                # 将关键词转换为正则表达式
                pattern = re.escape(keyword)
                patterns.append(pattern)
            
            if patterns:
                # 合并所有模式
                full_pattern = "|".join(patterns)
                self.compiled_patterns[mood_type] = re.compile(full_pattern)
    
    def analyze_text(self, text: str) -> MoodResult:
        """
        分析文本情感
        
        参数:
            text: 要分析的文本
            
        返回:
            心情分析结果
        """
        if not text or not text.strip():
            return MoodResult(
                mood_type=MoodType.NEUTRAL,
                confidence=0.0,
                triggers=[],
                reason="文本为空"
            )
        
        # 清理文本
        clean_text = self._clean_text(text)
        
        # 分析情感
        mood_scores = self._calculate_mood_scores(clean_text)
        
        # 获取最佳心情
        best_mood, confidence, triggers = self._get_best_mood(mood_scores)
        
        # 生成分析原因
        reason = self._generate_reason(best_mood, confidence, triggers, clean_text)
        
        return MoodResult(
            mood_type=best_mood,
            confidence=confidence,
            triggers=triggers,
            reason=reason
        )
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 转换为小写（中文不受影响）
        return text.lower()
    
    def _calculate_mood_scores(self, text: str) -> Dict[MoodType, float]:
        """计算各种心情的分数"""
        scores = {mood: 0.0 for mood in self.keyword_patterns.keys()}
        all_triggers = {mood: [] for mood in self.keyword_patterns.keys()}
        
        # 分割文本为句子
        sentences = re.split(r'[。！？!?;；]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            for mood_type, pattern in self.compiled_patterns.items():
                # 查找匹配
                matches = pattern.findall(sentence)
                if matches:
                    # 计算分数
                    base_score = len(matches) * self.keyword_patterns[mood_type]["weight"]
                    
                    # 检查否定词
                    has_negative = self._has_negative_prefix(sentence, matches)
                    if has_negative:
                        base_score *= 0.3  # 有否定词时降低分数
                    
                    # 检查强度词
                    intensity_factor = self._get_intensity_factor(sentence, matches)
                    base_score *= intensity_factor
                    
                    scores[mood_type] += base_score
                    all_triggers[mood_type].extend(matches)
        
        return scores
    
    def _has_negative_prefix(self, sentence: str, matches: List[str]) -> bool:
        """检查匹配前是否有否定词"""
        for match in matches:
            for negative in self.negative_words:
                # 检查否定词是否在匹配前
                pattern = f"{negative}.*?{re.escape(match)}"
                if re.search(pattern, sentence):
                    return True
        return False
    
    def _get_intensity_factor(self, sentence: str, matches: List[str]) -> float:
        """获取强度因子"""
        max_intensity = 1.0
        for match in matches:
            for intensity_word, factor in self.intensity_words.items():
                pattern = f"{intensity_word}.*?{re.escape(match)}"
                if re.search(pattern, sentence):
                    max_intensity = max(max_intensity, factor)
        return max_intensity
    
    def _get_best_mood(self, scores: Dict[MoodType, float]) -> Tuple[MoodType, float, List[str]]:
        """获取最佳心情"""
        if not scores or all(score == 0 for score in scores.values()):
            return MoodType.NEUTRAL, 0.0, []
        
        # 找到最高分
        best_mood = max(scores, key=scores.get)
        best_score = scores[best_mood]
        
        # 归一化置信度
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.0
        
        # 限制置信度在合理范围
        confidence = min(max(confidence, 0.0), 1.0)
        
        return best_mood, confidence, []
    
    def _generate_reason(self, mood_type: MoodType, confidence: float, triggers: List[str], text: str) -> str:
        """生成分析原因"""
        mood_names = {
            MoodType.HAPPY: "开心",
            MoodType.EXCITED: "兴奋",
            MoodType.SAD: "低落",
            MoodType.PROUD: "自豪",
            MoodType.CONFUSED: "困惑",
            MoodType.NEUTRAL: "中性"
        }
        
        mood_name = mood_names.get(mood_type, "未知")
        
        if confidence < 0.3:
            return f"情感倾向不明显，可能为{mood_name}状态"
        elif confidence < 0.6:
            return f"有一定{mood_name}倾向"
        elif confidence < 0.8:
            return f"比较{mood_name}"
        else:
            return f"非常{mood_name}"
    
    def analyze_conversation_context(self, messages: List[Dict[str, str]], window_size: int = 5) -> MoodResult:
        """
        分析对话上下文情感
        
        参数:
            messages: 消息列表
            window_size: 分析窗口大小
            
        返回:
            心情分析结果
        """
        if not messages:
            return MoodResult(
                mood_type=MoodType.NEUTRAL,
                confidence=0.0,
                triggers=[],
                reason="消息列表为空"
            )
        
        # 只分析最近的几条消息
        recent_messages = messages[-window_size:]
        
        # 合并所有消息内容
        combined_text = " ".join([msg.get("content", "") for msg in recent_messages])
        
        return self.analyze_text(combined_text)
    
    def get_mood_history_summary(self, mood_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取心情历史摘要
        
        参数:
            mood_history: 心情历史记录
            
        返回:
            心情摘要
        """
        if not mood_history:
            return {
                "total_moods": 0,
                "most_common_mood": "neutral",
                "mood_distribution": {},
                "average_confidence": 0.0
            }
        
        # 统计心情分布
        mood_counts = {}
        total_confidence = 0.0
        
        for record in mood_history:
            mood = record.get("mood", "neutral")
            confidence = record.get("confidence", 0.0)
            
            if mood not in mood_counts:
                mood_counts[mood] = {
                    "count": 0,
                    "total_confidence": 0.0
                }
            
            mood_counts[mood]["count"] += 1
            mood_counts[mood]["total_confidence"] += confidence
            total_confidence += confidence
        
        # 找到最常出现的心情
        most_common_mood = max(mood_counts.items(), key=lambda x: x[1]["count"])[0] if mood_counts else "neutral"
        
        # 计算平均置信度
        avg_confidence = total_confidence / len(mood_history) if mood_history else 0.0
        
        # 格式化分布
        mood_distribution = {}
        for mood, data in mood_counts.items():
            mood_distribution[mood] = {
                "count": data["count"],
                "percentage": (data["count"] / len(mood_history)) * 100,
                "avg_confidence": data["total_confidence"] / data["count"]
            }
        
        return {
            "total_moods": len(mood_history),
            "most_common_mood": most_common_mood,
            "mood_distribution": mood_distribution,
            "average_confidence": avg_confidence
        }

# 使用示例
if __name__ == "__main__":
    print("心情分析器测试")
    print("=" * 50)
    
    # 创建分析器
    analyzer = MoodAnalyzer()
    
    # 测试文本
    test_texts = [
        "我今天特别开心，因为我考试得了第一名！",
        "为什么会这样？我真的不明白。",
        "有点难过，今天下雨了，不能出去玩。",
        "我为我的成就感到非常自豪！",
        "哇！这真是太令人兴奋了！",
        "今天天气不错，心情一般。"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {text}")
        result = analyzer.analyze_text(text)
        print(f"  心情: {result.mood_type.value}")
        print(f"  置信度: {result.confidence:.2%}")
        print(f"  原因: {result.reason}")
    
    # 测试对话上下文
    print("\n" + "=" * 50)
    print("测试对话上下文分析")
    
    test_messages = [
        {"role": "user", "content": "我今天考试没考好..."},
        {"role": "assistant", "content": "别难过，下次努力就好！"},
        {"role": "user", "content": "嗯，我会加油的！"},
        {"role": "assistant", "content": "我相信你一定可以的！"}
    ]
    
    context_result = analyzer.analyze_conversation_context(test_messages)
    print(f"对话上下文心情: {context_result.mood_type.value}")
    print(f"置信度: {context_result.confidence:.2%}")
    
    print("=" * 50)
    print("心情分析器测试完成")