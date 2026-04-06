# 记忆读取系统
# 功能：负责读取和检索记忆

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import re

class MemoryRecall:
    """
    记忆读取类
    管理记忆的检索和查询
    """
    
    def __init__(self, storage_path: str = None):
        """
        初始化记忆读取
        
        参数:
            storage_path: 存储路径
        """
        from .storage import MemoryStorage
        
        self.storage = MemoryStorage(storage_path)
        self.conversation_cache = {}  # 对话缓存
        self.summary_cache = {}  # 摘要缓存
        self.cache_timeout = 300  # 缓存超时时间（秒）
        
        print(f"记忆读取系统初始化完成")
    
    def get_recent_conversations(self, 
                                limit: int = 10, 
                                offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取最近的对话
        
        参数:
            limit: 限制数量
            offset: 偏移量
            
        返回:
            对话列表
        """
        conversations = self.storage.list_conversations(limit, offset)
        
        # 丰富信息
        for conv in conversations:
            # 加载完整对话（如果缓存中没有）
            if conv["filename"] not in self.conversation_cache:
                full_data = self.storage.load_conversation(conv["filename"])
                if full_data:
                    # 缓存完整数据
                    self.conversation_cache[conv["filename"]] = {
                        "data": full_data,
                        "timestamp": time.time()
                    }
                    
                    # 提取预览
                    messages = full_data.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        conv["preview"] = last_message.get("content", "")[:50] + "..."
                        conv["last_message_time"] = last_message.get("timestamp", 0)
        
        return conversations
    
    def search_conversations(self, 
                           query: str, 
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索对话
        
        参数:
            query: 搜索关键词
            limit: 限制数量
            
        返回:
            匹配的对话列表
        """
        results = []
        
        # 获取所有对话文件
        conversations = self.storage.list_conversations(limit=1000)  # 获取大量对话
        
        for conv_info in conversations:
            filename = conv_info["filename"]
            
            # 从缓存或文件加载完整对话
            if filename in self.conversation_cache:
                conv_data = self.conversation_cache[filename]["data"]
            else:
                conv_data = self.storage.load_conversation(filename)
                if conv_data:
                    self.conversation_cache[filename] = {
                        "data": conv_data,
                        "timestamp": time.time()
                    }
            
            if not conv_data:
                continue
            
            # 搜索消息内容
            messages = conv_data.get("messages", [])
            matches = []
            
            for msg in messages:
                content = msg.get("content", "").lower()
                if query.lower() in content:
                    matches.append({
                        "role": msg.get("role", ""),
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", 0)
                    })
            
            if matches:
                # 计算相关性分数
                score = self._calculate_relevance_score(query, matches)
                
                result = {
                    "filename": filename,
                    "conversation_id": conv_info["conversation_id"],
                    "date": conv_info["date"],
                    "match_count": len(matches),
                    "score": score,
                    "matches": matches[:3],  # 只显示前3个匹配
                    "metadata": conv_data.get("metadata", {})
                }
                results.append(result)
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:limit]
    
    def _calculate_relevance_score(self, query: str, matches: List[Dict[str, Any]]) -> float:
        """
        计算相关性分数
        
        参数:
            query: 查询词
            matches: 匹配的消息
            
        返回:
            相关性分数
        """
        if not matches:
            return 0.0
        
        # 基础分数：匹配数量
        base_score = len(matches) * 10
        
        # 新鲜度分数：越新的对话分数越高
        latest_timestamp = max(match.get("timestamp", 0) for match in matches)
        current_time = time.time()
        time_diff = current_time - latest_timestamp
        
        if time_diff < 3600:  # 1小时内
            freshness_score = 50
        elif time_diff < 86400:  # 24小时内
            freshness_score = 30
        elif time_diff < 604800:  # 7天内
            freshness_score = 20
        else:
            freshness_score = 10
        
        # 查询长度分数：长查询更有价值
        query_length_score = min(len(query) * 2, 20)
        
        return base_score + freshness_score + query_length_score
    
    def get_conversation_context(self, 
                               conversation_id: str, 
                               context_length: int = 5) -> List[Dict[str, Any]]:
        """
        获取对话上下文
        
        参数:
            conversation_id: 对话ID
            context_length: 上下文长度
            
        返回:
            上下文消息列表
        """
        # 首先尝试从缓存获取
        cached_data = self._get_from_cache(conversation_id)
        if cached_data:
            messages = cached_data.get("messages", [])
            return messages[-context_length:] if messages else []
        
        # 从文件加载
        conversations = self.storage.list_conversations(limit=100)
        for conv_info in conversations:
            if conv_info["conversation_id"] == conversation_id:
                conv_data = self.storage.load_conversation(conv_info["filename"])
                if conv_data:
                    # 添加到缓存
                    self.conversation_cache[conv_info["filename"]] = {
                        "data": conv_data,
                        "timestamp": time.time()
                    }
                    
                    messages = conv_data.get("messages", [])
                    return messages[-context_length:] if messages else []
        
        return []
    
    def _get_from_cache(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取对话数据
        
        参数:
            conversation_id: 对话ID
            
        返回:
            对话数据
        """
        # 查找缓存中的对话
        for filename, cache_data in self.conversation_cache.items():
            data = cache_data["data"]
            cache_time = cache_data["timestamp"]
            
            # 检查缓存是否过期
            if time.time() - cache_time > self.cache_timeout:
                continue
            
            if data.get("conversation_id") == conversation_id:
                return data
        
        return None
    
    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """
        获取每日摘要
        
        参数:
            date: 日期 (YYYY-MM-DD)，None则使用今天
            
        返回:
            每日摘要
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 获取当天的对话
        conversations = self.storage.list_conversations(limit=100)
        daily_conversations = []
        
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        for conv_info in conversations:
            conv_date_str = conv_info.get("date", "")
            if not conv_date_str:
                continue
            
            try:
                conv_date = datetime.fromisoformat(conv_date_str.replace("Z", "+00:00"))
                if conv_date.date() == target_date.date():
                    daily_conversations.append(conv_info)
            except:
                continue
        
        # 统计信息
        total_messages = 0
        conversation_count = len(daily_conversations)
        
        for conv_info in daily_conversations:
            total_messages += conv_info.get("message_count", 0)
        
        summary = {
            "date": date,
            "conversation_count": conversation_count,
            "total_messages": total_messages,
            "average_messages_per_conversation": round(total_messages / max(conversation_count, 1), 1),
            "conversations": daily_conversations[:10]  # 只显示前10个
        }
        
        return summary
    
    def get_conversation_stats(self, 
                              days: int = 7) -> Dict[str, Any]:
        """
        获取对话统计
        
        参数:
            days: 统计天数
            
        返回:
            统计信息
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conversations = self.storage.list_conversations(limit=1000)
        
        daily_stats = {}
        mood_stats = {}
        total_conversations = 0
        total_messages = 0
        
        for conv_info in conversations:
            conv_date_str = conv_info.get("date", "")
            if not conv_date_str:
                continue
            
            try:
                conv_date = datetime.fromisoformat(conv_date_str.replace("Z", "+00:00"))
                
                # 检查是否在时间范围内
                if start_date <= conv_date <= end_date:
                    # 每日统计
                    date_key = conv_date.strftime("%Y-%m-%d")
                    if date_key not in daily_stats:
                        daily_stats[date_key] = {
                            "conversations": 0,
                            "messages": 0
                        }
                    
                    daily_stats[date_key]["conversations"] += 1
                    daily_stats[date_key]["messages"] += conv_info.get("message_count", 0)
                    
                    # 心情统计
                    metadata = conv_info.get("metadata", {})
                    mood = metadata.get("mood", "unknown")
                    if mood not in mood_stats:
                        mood_stats[mood] = 0
                    mood_stats[mood] += 1
                    
                    total_conversations += 1
                    total_messages += conv_info.get("message_count", 0)
                    
            except:
                continue
        
        # 整理每日统计
        date_list = []
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            date_list.append(date)
        
        daily_stats_sorted = []
        for date in date_list:
            stats = daily_stats.get(date, {"conversations": 0, "messages": 0})
            daily_stats_sorted.append({
                "date": date,
                "conversations": stats["conversations"],
                "messages": stats["messages"]
            })
        
        return {
            "period": f"{days}天",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "average_messages_per_day": round(total_messages / max(days, 1), 1),
            "daily_stats": daily_stats_sorted,
            "mood_stats": mood_stats
        }
    
    def cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_files = []
        
        for filename, cache_data in list(self.conversation_cache.items()):
            if current_time - cache_data["timestamp"] > self.cache_timeout:
                expired_files.append(filename)
        
        for filename in expired_files:
            del self.conversation_cache[filename]
        
        if expired_files:
            print(f"🗑️ 清理了 {len(expired_files)} 个过期缓存")
    
    def export_conversations(self, 
                           output_path: str, 
                           format: str = "json") -> bool:
        """
        导出对话记录
        
        参数:
            output_path: 输出路径
            format: 导出格式 (json, txt)
            
        返回:
            是否导出成功
        """
        try:
            conversations = self.storage.list_conversations(limit=1000)
            
            if format == "json":
                export_data = {
                    "export_time": datetime.now().isoformat(),
                    "conversation_count": len(conversations),
                    "conversations": []
                }
                
                for conv_info in conversations:
                    conv_data = self.storage.load_conversation(conv_info["filename"])
                    if conv_data:
                        export_data["conversations"].append(conv_data)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            elif format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"对话记录导出 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for conv_info in conversations:
                        conv_data = self.storage.load_conversation(conv_info["filename"])
                        if conv_data:
                            f.write(f"对话ID: {conv_info['conversation_id']}\n")
                            f.write(f"时间: {conv_info['date']}\n")
                            f.write(f"消息数: {conv_info['message_count']}\n")
                            f.write("-" * 30 + "\n")
                            
                            for msg in conv_data.get("messages", []):
                                role = "你" if msg.get("role") == "user" else "AI"
                                content = msg.get("content", "")
                                f.write(f"{role}: {content}\n")
                            
                            f.write("\n" + "=" * 50 + "\n\n")
            
            print(f"✅ 对话导出成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出对话失败: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    print("记忆读取系统测试")
    print("=" * 50)
    
    # 创建读取实例
    recall = MemoryRecall()
    
    # 测试获取最近对话
    print("获取最近对话...")
    recent_convs = recall.get_recent_conversations(limit=5)
    print(f"找到 {len(recent_convs)} 个最近对话")
    
    for conv in recent_convs[:2]:  # 只显示前2个
        print(f"  - {conv.get('date')}: {conv.get('conversation_id')} ({conv.get('message_count')} 条消息)")
    
    # 测试搜索
    print("\n测试搜索功能...")
    search_results = recall.search_conversations("你好", limit=3)
    print(f"搜索到 {len(search_results)} 个结果")
    
    for result in search_results:
        print(f"  - {result.get('conversation_id')}: {result.get('match_count')} 个匹配")
    
    # 测试统计
    print("\n测试统计功能...")
    stats = recall.get_conversation_stats(days=3)
    print(f"3天统计: {stats.get('total_conversations')} 个对话, {stats.get('total_messages')} 条消息")
    
    # 测试每日摘要
    print("\n测试每日摘要...")
    today = datetime.now().strftime("%Y-%m-%d")
    daily_summary = recall.get_daily_summary(today)
    print(f"今日摘要: {daily_summary.get('conversation_count')} 个对话")
    
    print("=" * 50)
    print("记忆读取系统测试完成")