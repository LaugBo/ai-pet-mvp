# 记忆优化器
# 功能：优化记忆存储，生成摘要，智能管理记忆

import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import jieba
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path  # 添加这行导入

@dataclass
class ConversationSummary:
    """对话摘要"""
    conversation_id: str
    summary: str
    keywords: List[str]
    topics: List[str]
    mood_summary: Dict[str, float]
    message_count: int
    created_at: datetime
    updated_at: datetime
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "conversation_id": self.conversation_id,
            "summary": self.summary,
            "keywords": self.keywords,
            "topics": self.topics,
            "mood_summary": self.mood_summary,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSummary':
        """从字典创建"""
        return cls(
            conversation_id=data["conversation_id"],
            summary=data["summary"],
            keywords=data["keywords"],
            topics=data["topics"],
            mood_summary=data["mood_summary"],
            message_count=data["message_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data.get("version", 1)
        )

class MemoryOptimizer:
    """
    记忆优化器
    智能管理记忆，生成摘要，优化存储
    """
    
    def __init__(self, storage_path: str = None, max_workers: int = 4):
        """
        初始化记忆优化器
        
        参数:
            storage_path: 存储路径
            max_workers: 最大工作线程数
        """
        from .storage import MemoryStorage
        from .recall import MemoryRecall
        
        self.storage = MemoryStorage(storage_path)
        self.recall = MemoryRecall(storage_path)
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.optimization_lock = threading.Lock()
        
        # 配置
        self.config = {
            "max_conversation_length": 50,  # 最大对话长度
            "summary_interval": 10,  # 摘要生成间隔（消息数）
            "min_keyword_frequency": 2,  # 最小关键词频率
            "max_keywords": 10,  # 最大关键词数
            "compression_threshold": 100,  # 压缩阈值（消息数）
            "auto_cleanup_days": 30,  # 自动清理天数
            "backup_enabled": True,  # 启用备份
            "backup_interval_hours": 24,  # 备份间隔（小时）
        }
        
        # 缓存
        self.summary_cache = {}  # 摘要缓存
        self.keyword_cache = {}  # 关键词缓存
        
        # 初始化jieba
        self._init_jieba()
        
        print(f"记忆优化器初始化完成")
        print(f"最大工作线程: {max_workers}")
        print(f"自动清理: {self.config['auto_cleanup_days']}天")
    
    def _init_jieba(self):
        """初始化jieba分词"""
        try:
            # 添加自定义词典
            custom_words = [
                "AI宠物", "心情", "记忆", "对话", "聊天",
                "开心", "兴奋", "低落", "自豪", "困惑",
                "你好", "再见", "谢谢", "不客气", "对不起"
            ]
            for word in custom_words:
                jieba.add_word(word)
            
            # 加载停用词
            self.stopwords = self._load_stopwords()
            
        except Exception as e:
            print(f"⚠️ 初始化jieba失败: {e}")
            self.stopwords = set()
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        # 中文停用词
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就",
            "不", "人", "都", "一", "一个", "上", "也", "很",
            "到", "说", "要", "去", "你", "会", "着", "没有",
            "看", "好", "自己", "这", "那", "啊", "嗯", "哦"
        }
        return stopwords
    
    def generate_summary(self, conversation_data: Dict[str, Any]) -> ConversationSummary:
        """
        生成对话摘要
        
        参数:
            conversation_data: 对话数据
            
        返回:
            对话摘要
        """
        conversation_id = conversation_data.get("conversation_id", "")
        messages = conversation_data.get("messages", [])
        metadata = conversation_data.get("metadata", {})
        
        if not messages:
            return ConversationSummary(
                conversation_id=conversation_id,
                summary="空对话",
                keywords=[],
                topics=[],
                mood_summary={},
                message_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        # 提取对话内容
        conversation_text = self._extract_conversation_text(messages)
        
        # 生成摘要
        summary = self._generate_text_summary(conversation_text)
        
        # 提取关键词
        keywords = self._extract_keywords(conversation_text)
        
        # 提取主题
        topics = self._extract_topics(conversation_text)
        
        # 分析心情
        mood_summary = self._analyze_conversation_mood(messages, metadata)
        
        return ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            keywords=keywords,
            topics=topics,
            mood_summary=mood_summary,
            message_count=len(messages),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _extract_conversation_text(self, messages: List[Dict[str, Any]]) -> str:
        """提取对话文本"""
        text_parts = []
        for msg in messages:
            if isinstance(msg, dict) and "content" in msg:
                content = msg["content"]
                if content and isinstance(content, str):
                    text_parts.append(content.strip())
        
        return " ".join(text_parts)
    
    def _generate_text_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成文本摘要
        
        参数:
            text: 文本
            max_length: 最大长度
            
        返回:
            摘要文本
        """
        if not text or len(text) < 50:
            return text
        
        try:
            # 简单的摘要算法：提取关键句子
            sentences = re.split(r'[。！？!?;；]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 3:
                return text
            
            # 评分句子
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = 0
                
                # 位置权重
                if i == 0 or i == len(sentences) - 1:
                    score += 2
                
                # 长度权重
                if 10 <= len(sentence) <= 50:
                    score += 1
                
                # 问句权重
                if any(q in sentence for q in ["?", "？", "什么", "为什么", "怎么", "如何"]):
                    score += 1
                
                # 情感词权重
                emotion_words = ["开心", "高兴", "难过", "伤心", "生气", "喜欢", "爱", "讨厌"]
                for word in emotion_words:
                    if word in sentence:
                        score += 1
                        break
                
                scored_sentences.append((sentence, score))
            
            # 选择高分句子
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            selected = [s[0] for s in scored_sentences[:3]]
            
            summary = "。".join(selected) + "。"
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            print(f"❌ 生成摘要失败: {e}")
            return text[:max_length] + ("..." if len(text) > max_length else "")
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        提取关键词
        
        参数:
            text: 文本
            top_n: 关键词数量
            
        返回:
            关键词列表
        """
        if not text:
            return []
        
        try:
            # 使用jieba分词
            words = jieba.lcut(text)
            
            # 过滤
            filtered_words = []
            for word in words:
                word = word.strip()
                if (len(word) >= 2 and  # 至少2个字符
                    word not in self.stopwords and
                    not word.isdigit() and
                    not re.match(r'^[^\u4e00-\u9fa5]+$', word)):  # 非纯符号
                    filtered_words.append(word)
            
            # 统计词频
            word_counts = Counter(filtered_words)
            
            # 过滤低频词
            filtered_counts = {word: count for word, count in word_counts.items() 
                              if count >= self.config["min_keyword_frequency"]}
            
            # 排序并取前N个
            sorted_words = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, _ in sorted_words[:top_n]]
            
            return keywords
            
        except Exception as e:
            print(f"❌ 提取关键词失败: {e}")
            return []
    
    def _extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        提取主题
        
        参数:
            text: 文本
            max_topics: 最大主题数
            
        返回:
            主题列表
        """
        # 简单的主题提取：基于常见话题
        topics = set()
        
        topic_patterns = {
            "学习": ["学习", "考试", "作业", "学校", "老师", "课程"],
            "工作": ["工作", "上班", "公司", "项目", "会议", "任务"],
            "生活": ["吃饭", "睡觉", "运动", "健康", "家庭", "朋友"],
            "娱乐": ["电影", "音乐", "游戏", "旅游", "看书", "购物"],
            "情感": ["开心", "难过", "生气", "喜欢", "爱", "想念"],
            "科技": ["电脑", "手机", "网络", "软件", "AI", "数据"],
            "天气": ["天气", "下雨", "晴天", "温度", "季节", "气候"]
        }
        
        for topic, keywords in topic_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    topics.add(topic)
                    break
        
        return list(topics)[:max_topics]
    
    def _analyze_conversation_mood(self, messages: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, float]:
        """
        分析对话心情
        
        参数:
            messages: 消息列表
            metadata: 元数据
            
        返回:
            心情分布
        """
        # 从元数据获取心情
        if "mood" in metadata:
            mood = metadata["mood"]
            if isinstance(mood, str):
                return {mood: 1.0}
        
        # 分析消息中的情感词
        mood_words = {
            "happy": ["开心", "高兴", "快乐", "哈哈", "嘻嘻", "喜欢", "爱"],
            "sad": ["难过", "伤心", "哭", "唉", "失望", "失落"],
            "angry": ["生气", "愤怒", "讨厌", "恨", "烦"],
            "excited": ["兴奋", "激动", "惊喜", "哇", "太棒了"],
            "confused": ["困惑", "疑惑", "不明白", "不懂", "为什么"]
        }
        
        mood_counts = {mood: 0 for mood in mood_words.keys()}
        total_count = 0
        
        for msg in messages:
            if isinstance(msg, dict) and "content" in msg:
                content = msg["content"]
                if isinstance(content, str):
                    for mood, words in mood_words.items():
                        for word in words:
                            if word in content:
                                mood_counts[mood] += 1
                                total_count += 1
        
        # 计算比例
        if total_count > 0:
            mood_summary = {mood: count/total_count for mood, count in mood_counts.items()}
        else:
            mood_summary = {mood: 0.0 for mood in mood_counts.keys()}
        
        return mood_summary
    
    def optimize_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化对话数据
        
        参数:
            conversation_data: 原始对话数据
            
        返回:
            优化后的对话数据
        """
        conversation_id = conversation_data.get("conversation_id", "")
        messages = conversation_data.get("messages", [])
        
        if len(messages) <= self.config["max_conversation_length"]:
            return conversation_data
        
        # 生成摘要
        with self.optimization_lock:
            if conversation_id in self.summary_cache:
                summary_data = self.summary_cache[conversation_id]
            else:
                summary_data = self.generate_summary(conversation_data)
                self.summary_cache[conversation_id] = summary_data
        
        # 压缩消息
        if len(messages) > self.config["compression_threshold"]:
            compressed_messages = self._compress_messages(messages)
            
            optimized_data = conversation_data.copy()
            optimized_data["messages"] = compressed_messages
            optimized_data["optimized"] = True
            optimized_data["original_count"] = len(messages)
            optimized_data["compressed_count"] = len(compressed_messages)
            optimized_data["compression_ratio"] = len(compressed_messages) / len(messages)
            optimized_data["summary"] = summary_data.to_dict()
            
            return optimized_data
        
        return conversation_data
    
    def _compress_messages(self, messages: List[Dict[str, Any]], ratio: float = 0.5) -> List[Dict[str, Any]]:
        """
        压缩消息
        
        参数:
            messages: 消息列表
            ratio: 压缩比例
            
        返回:
            压缩后的消息列表
        """
        if not messages or ratio >= 1.0:
            return messages
        
        # 保留重要消息
        important_messages = []
        
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            
            # 判断重要性
            importance_score = 0
            
            # 用户消息通常更重要
            if msg.get("role") == "user":
                importance_score += 2
            
            # 开头和结尾的消息
            if i < 3 or i > len(messages) - 3:
                importance_score += 1
            
            # 包含情感词
            emotion_words = ["重要", "关键", "主要", "特别", "非常", "最"]
            for word in emotion_words:
                if word in content:
                    importance_score += 1
            
            # 长消息
            if len(content) > 20:
                importance_score += 1
            
            # 包含问号
            if "?" in content or "？" in content:
                importance_score += 1
            
            if importance_score >= 2:
                important_messages.append(msg)
        
        # 如果重要消息太少，按间隔采样
        target_count = max(1, int(len(messages) * ratio))
        
        if len(important_messages) < target_count:
            step = len(messages) // target_count
            sampled_messages = []
            
            for i in range(0, len(messages), step):
                if i < len(messages) and len(sampled_messages) < target_count:
                    sampled_messages.append(messages[i])
            
            return sampled_messages
        
        return important_messages[:target_count]
    
    def batch_optimize(self, conversation_ids: List[str] = None) -> Dict[str, Any]:
        """
        批量优化对话
        
        参数:
            conversation_ids: 对话ID列表，None则优化所有
            
        返回:
            优化结果统计
        """
        start_time = time.time()
        
        if conversation_ids is None:
            # 获取所有对话
            conversations = self.storage.list_conversations(limit=1000)
            conversation_ids = [conv["conversation_id"] for conv in conversations]
        
        results = {
            "total": len(conversation_ids),
            "optimized": 0,
            "skipped": 0,
            "failed": 0,
            "compression_ratios": [],
            "execution_time": 0.0
        }
        
        # 并行处理
        futures = []
        for conv_id in conversation_ids:
            future = self.executor.submit(self._optimize_single, conv_id)
            futures.append(future)
        
        # 收集结果
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)
                if result["optimized"]:
                    results["optimized"] += 1
                    if "compression_ratio" in result:
                        results["compression_ratios"].append(result["compression_ratio"])
                else:
                    results["skipped"] += 1
            except Exception as e:
                print(f"❌ 优化对话失败: {e}")
                results["failed"] += 1
        
        # 计算统计
        if results["compression_ratios"]:
            results["avg_compression_ratio"] = sum(results["compression_ratios"]) / len(results["compression_ratios"])
        else:
            results["avg_compression_ratio"] = 0.0
        
        results["execution_time"] = time.time() - start_time
        
        print(f"✅ 批量优化完成:")
        print(f"   总数: {results['total']}")
        print(f"   优化: {results['optimized']}")
        print(f"   跳过: {results['skipped']}")
        print(f"   失败: {results['failed']}")
        print(f"   平均压缩率: {results.get('avg_compression_ratio', 0):.2%}")
        print(f"   执行时间: {results['execution_time']:.2f}秒")
        
        return results
    
    def _optimize_single(self, conversation_id: str) -> Dict[str, Any]:
        """优化单个对话"""
        try:
            # 查找对话文件
            conversations = self.storage.list_conversations(limit=1000)
            target_file = None
            
            for conv in conversations:
                if conv["conversation_id"] == conversation_id:
                    # 查找具体的文件
                    files = self.storage.conversations_path.glob(f"*{conversation_id}*.json")
                    for file in files:
                        target_file = file
                        break
                    break
            
            if not target_file or not target_file.exists():
                return {"conversation_id": conversation_id, "optimized": False, "reason": "文件不存在"}
            
            # 加载对话
            with open(target_file, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            # 检查是否需要优化
            messages = conversation_data.get("messages", [])
            if len(messages) <= self.config["max_conversation_length"]:
                return {"conversation_id": conversation_id, "optimized": False, "reason": "无需优化"}
            
            # 优化
            optimized_data = self.optimize_conversation(conversation_data)
            
            if optimized_data.get("optimized", False):
                # 保存优化后的数据
                backup_file = target_file.with_suffix(".json.backup")
                
                # 创建备份
                import shutil
                shutil.copy2(target_file, backup_file)
                
                # 保存优化版本
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(optimized_data, f, indent=2, ensure_ascii=False)
                
                compression_ratio = optimized_data.get("compression_ratio", 1.0)
                
                return {
                    "conversation_id": conversation_id,
                    "optimized": True,
                    "compression_ratio": compression_ratio,
                    "original_size": len(messages),
                    "optimized_size": len(optimized_data.get("messages", []))
                }
            
            return {"conversation_id": conversation_id, "optimized": False, "reason": "优化条件不满足"}
            
        except Exception as e:
            print(f"❌ 优化单个对话失败 {conversation_id}: {e}")
            return {"conversation_id": conversation_id, "optimized": False, "reason": str(e)}
    
    def cleanup_old_conversations(self, days: int = None) -> Dict[str, Any]:
        """
        清理旧对话
        
        参数:
            days: 保留天数
            
        返回:
            清理结果
        """
        if days is None:
            days = self.config["auto_cleanup_days"]
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        conversations = self.storage.list_conversations(limit=1000)
        deleted_count = 0
        total_size = 0
        
        for conv in conversations:
            if conv["timestamp"] < cutoff_time:
                # 查找文件
                files = self.storage.conversations_path.glob(f"*{conv['conversation_id']}*.json")
                for file in files:
                    try:
                        file_size = file.stat().st_size
                        file.unlink()
                        deleted_count += 1
                        total_size += file_size
                        print(f"🗑️ 删除旧对话: {file.name} ({conv['date']})")
                    except Exception as e:
                        print(f"❌ 删除文件失败 {file.name}: {e}")
        
        return {
            "deleted_count": deleted_count,
            "total_size": total_size,
            "days": days
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        返回:
            统计信息
        """
        conversations = self.storage.list_conversations(limit=1000)
        
        if not conversations:
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "avg_messages": 0.0,
                "storage_size": 0
            }
        
        total_messages = 0
        total_size = 0
        
        for conv in conversations:
            total_messages += conv.get("message_count", 0)
            total_size += conv.get("file_size", 0)
        
        return {
            "total_conversations": len(conversations),
            "total_messages": total_messages,
            "avg_messages": total_messages / len(conversations) if conversations else 0.0,
            "storage_size": total_size,
            "storage_size_mb": total_size / (1024 * 1024)
        }
    
    def backup_memories(self, backup_path: str = None) -> Dict[str, Any]:
        """
        备份记忆
        
        参数:
            backup_path: 备份路径
            
        返回:
            备份结果
        """
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = self.storage.storage_path / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"memory_backup_{timestamp}.json"
            else:
                backup_path = Path(backup_path)
            
            # 收集所有对话
            conversations = self.storage.list_conversations(limit=10000)
            backup_data = {
                "backup_time": datetime.now().isoformat(),
                "total_conversations": len(conversations),
                "conversations": []
            }
            
            for conv_info in conversations:
                try:
                    conv_data = self.storage.load_conversation(conv_info["filename"])
                    if conv_data:
                        backup_data["conversations"].append(conv_data)
                except Exception as e:
                    print(f"⚠️ 加载对话失败 {conv_info['filename']}: {e}")
            
            # 保存备份
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            backup_size = backup_path.stat().st_size
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "conversation_count": len(backup_data["conversations"]),
                "backup_size": backup_size,
                "backup_size_mb": backup_size / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_from_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        从备份恢复
        
        参数:
            backup_path: 备份文件路径
            
        返回:
            恢复结果
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return {"success": False, "error": "备份文件不存在"}
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            restored_count = 0
            failed_count = 0
            
            for conv_data in backup_data.get("conversations", []):
                try:
                    conversation_id = conv_data.get("conversation_id")
                    if conversation_id:
                        # 生成文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"conv_{conversation_id}_{timestamp}.json"
                        filepath = self.storage.conversations_path / filename
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(conv_data, f, indent=2, ensure_ascii=False)
                        
                        restored_count += 1
                except Exception as e:
                    print(f"❌ 恢复对话失败: {e}")
                    failed_count += 1
            
            return {
                "success": True,
                "restored_count": restored_count,
                "failed_count": failed_count,
                "total_count": len(backup_data.get("conversations", []))
            }
            
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """关闭优化器"""
        self.executor.shutdown(wait=True)
        print("✅ 记忆优化器已关闭")

# 使用示例
if __name__ == "__main__":
    print("记忆优化器测试")
    print("=" * 50)
    
    # 创建优化器
    optimizer = MemoryOptimizer(max_workers=2)
    
    # 获取统计信息
    stats = optimizer.get_statistics()
    print(f"存储统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 测试生成摘要
    test_conversation = {
        "conversation_id": "test_001",
        "messages": [
            {"role": "user", "content": "今天天气真好，心情特别开心！"},
            {"role": "assistant", "content": "是啊，天气好的时候出去走走很不错。"},
            {"role": "user", "content": "你有什么推荐的娱乐活动吗？"},
            {"role": "assistant", "content": "可以去看电影，或者去公园散步。"}
        ],
        "metadata": {"mood": "happy"}
    }
    
    print("\n测试生成摘要...")
    summary = optimizer.generate_summary(test_conversation)
    print(f"摘要: {summary.summary}")
    print(f"关键词: {summary.keywords}")
    print(f"主题: {summary.topics}")
    print(f"心情分布: {summary.mood_summary}")
    
    # 测试优化对话
    print("\n测试优化对话...")
    optimized = optimizer.optimize_conversation(test_conversation)
    print(f"优化结果: {optimized.get('optimized', False)}")
    
    # 清理
    optimizer.close()
    
    print("=" * 50)
    print("记忆优化器测试完成")