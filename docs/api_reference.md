#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI宠物MVP基础使用示例
展示如何以编程方式使用核心模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.ai.adapter import AIManager
from src.core.mood.manager import MoodManager
from src.core.mood.analyzer import MoodAnalyzer, MoodType
from src.core.memory.storage import MemoryStorage
from src.core.memory.recall import MemoryRecall
from src.utils.config import get_config_manager
from src.utils.logger import get_logger, info, error
from src.utils.helpers import Timer, safe_execute
from src.utils.error_handler import safe_call


def example_ai_interaction():
    """示例1: AI交互"""
    print("=" * 60)
    print("示例1: AI交互")
    print("=" * 60)
    
    # 1. 创建AI配置
    ai_config = {
        "adapter_type": "ollama",
        "ip": "localhost",  # 或你的Ollama服务器IP
        "port": 11434,
        "model": "qwen:7b",  # 或你安装的模型
        "timeout": 30
    }
    
    # 2. 创建AI管理器
    ai_manager = AIManager(ai_config)
    
    # 3. 连接AI
    print("连接AI...")
    if ai_manager.connect():
        print("✅ AI连接成功")
        
        # 4. 与AI对话
        with Timer("AI对话"):
            response = ai_manager.generate_response("你好，请介绍一下你自己")
            print(f"🤖 AI回复: {response}")
        
        # 5. 断开连接
        ai_manager.disconnect()
        print("✅ AI连接已断开")
    else:
        print("❌ AI连接失败，请检查:")
        print("   1. Ollama服务是否运行")
        print("   2. IP地址是否正确")
        print("   3. 网络连接是否正常")
    
    return ai_manager


def example_mood_analysis():
    """示例2: 心情分析"""
    print("\n" + "=" * 60)
    print("示例2: 心情分析")
    print("=" * 60)
    
    # 1. 创建心情管理器
    mood_manager = MoodManager()
    
    # 2. 定义心情变化回调
    def on_mood_change(old_mood, new_result):
        print(f"🎭 心情变化: {old_mood.value} -> {new_result.mood_type.value}")
        print(f"   原因: {new_result.reason}")
        print(f"   置信度: {new_result.confidence:.1%}")
    
    mood_manager.register_mood_change_callback(on_mood_change)
    
    # 3. 分析不同的文本
    test_texts = [
        "我今天很开心，天气真好！",
        "我很难过，今天遇到了不好的事情。",
        "今天星期三，普通的一天。",
        "我真的生气了，这太不公平了！"
    ]
    
    for text in test_texts:
        print(f"\n分析文本: '{text}'")
        with Timer("心情分析"):
            result = mood_manager.analyze_and_update(text)
            if result:
                current = mood_manager.current_mood
                print(f"   当前心情: {current.value} ({current.emoji})")
    
    # 4. 获取心情统计
    stats = mood_manager.get_mood_stats()
    print(f"\n📊 心情统计: 共分析 {stats['total']} 次")
    
    return mood_manager


def example_memory_storage():
    """示例3: 记忆存储"""
    print("\n" + "=" * 60)
    print("示例3: 记忆存储")
    print("=" * 60)
    
    # 1. 创建记忆存储
    memory_storage = MemoryStorage()
    print("✅ 记忆存储初始化完成")
    
    # 2. 保存对话
    conversations = [
        {
            "user": "你好，AI宠物",
            "ai": "你好！我是你的AI宠物，今天心情很好！",
            "timestamp": "2024-01-01T10:00:00",
            "mood": "happy"
        },
        {
            "user": "今天天气怎么样？",
            "ai": "虽然我看不到窗外，但我能感受到你的好心情！",
            "timestamp": "2024-01-01T10:05:00",
            "mood": "happy"
        },
        {
            "user": "我有点难过...",
            "ai": "别难过，我会一直陪着你的。",
            "timestamp": "2024-01-01T10:10:00",
            "mood": "sad"
        }
    ]
    
    for conv in conversations:
        result = memory_storage.save_conversation(conv)
        if result:
            print(f"💾 保存对话: '{conv['user'][:20]}...'")
    
    # 3. 获取对话数量
    count = memory_storage.get_conversation_count()
    print(f"📁 存储的对话数量: {count}")
    
    # 4. 获取最近的对话
    recent = memory_storage.get_recent_conversations(limit=2)
    print(f"\n最近{len(recent)}条对话:")
    for i, conv in enumerate(recent, 1):
        print(f"  {i}. 用户: {conv['user']}")
        print(f"     AI: {conv['ai']}")
        print(f"     心情: {conv.get('mood', '未知')}")
    
    # 5. 保存心情记录
    mood_data = {
        "mood": "happy",
        "reason": "用户说了开心的话",
        "confidence": 0.85
    }
    memory_storage.save_mood(mood_data)
    print("💾 心情记录已保存")
    
    return memory_storage


def example_memory_search():
    """示例4: 记忆搜索"""
    print("\n" + "=" * 60)
    print("示例4: 记忆搜索")
    print("=" * 60)
    
    # 1. 创建记忆存储
    storage = MemoryStorage()
    
    # 2. 创建记忆读取器
    recall = MemoryRecall(storage)
    
    # 3. 获取统计信息
    stats = recall.get_statistics()
    print(f"📊 记忆统计:")
    print(f"   对话数量: {stats.get('conversation_count', 0)}")
    print(f"   心情记录: {stats.get('mood_count', 0)}")
    print(f"   总大小: {stats.get('total_size_formatted', '0B')}")
    
    # 4. 搜索对话（如果有数据的话）
    conversations = storage.get_recent_conversations(limit=5)
    if conversations:
        # 模拟搜索
        print(f"\n🔍 搜索'开心'相关对话:")
        for conv in conversations:
            if "开心" in conv.get("user", "") or "开心" in conv.get("ai", ""):
                print(f"  - 用户: {conv['user']}")
    
    return recall


def example_config_management():
    """示例5: 配置管理"""
    print("\n" + "=" * 60)
    print("示例5: 配置管理")
    print("=" * 60)
    
    # 1. 获取配置管理器
    config_manager = get_config_manager()
    print("✅ 配置管理器初始化完成")
    
    # 2. 创建示例配置
    example_config = {
        "app": {
            "name": "AI宠物MVP",
            "version": "1.0.0",
            "debug": False
        },
        "user": {
            "name": "示例用户",
            "preferences": {
                "theme": "dark",
                "language": "zh-CN"
            }
        }
    }
    
    # 3. 保存配置
    result = config_manager.save_config("example_config.json", example_config)
    if result:
        print("💾 配置保存成功")
    
    # 4. 加载配置
    loaded_config = config_manager.load_config("example_config.json")
    if loaded_config:
        print("📂 配置加载成功")
        print(f"   应用名称: {loaded_config.get('app', {}).get('name')}")
        print(f"   用户主题: {loaded_config.get('user', {}).get('preferences', {}).get('theme')}")
    
    return config_manager


def example_logging_system():
    """示例6: 日志系统"""
    print("\n" + "=" * 60)
    print("示例6: 日志系统")
    print("=" * 60)
    
    # 1. 获取日志器
    logger = get_logger("example", "DEBUG")
    
    # 2. 记录不同级别的日志
    logger.debug("这是一条调试信息")
    logger.info("应用程序启动", version="1.0.0", user="example")
    logger.warning("磁盘空间不足", free_space="500MB")
    
    # 3. 记录错误（带异常）
    try:
        x = 1 / 0
    except Exception as e:
        logger.error("数学运算错误", error=str(e))
    
    # 4. 快捷函数
    info("使用快捷函数记录信息", action="test")
    error("使用快捷函数记录错误", code=1001)
    
    # 5. 记录系统信息
    logger.log_system_info()
    
    print("✅ 日志记录完成，请查看 logs/ 目录")
    
    return logger


def example_error_handling():
    """示例7: 错误处理"""
    print("\n" + "=" * 60)
    print("示例7: 错误处理")
    print("=" * 60)
    
    from src.utils.error_handler import get_error_handler, safe_call, AIError, ErrorCode
    
    # 1. 获取错误处理器
    error_handler = get_error_handler()
    
    # 2. 安全执行示例
    def risky_operation(filename):
        """可能失败的操作"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件不存在: {filename}")
        return f"成功读取 {filename}"
    
    # 使用安全执行
    result = error_handler.safe_execute(
        lambda: risky_operation("nonexistent.txt"),
        operation="读取文件",
        default_return="默认值",
        raise_exception=False
    )
    print(f"安全执行结果: {result}")
    
    # 3. 使用装饰器
    @safe_call(operation="装饰器示例", default_return="装饰器默认值")
    def decorated_function():
        raise ValueError("装饰器测试错误")
    
    result = decorated_function()
    print(f"装饰器函数结果: {result}")
    
    # 4. 手动错误处理
    try:
        raise RuntimeError("手动抛出错误")
    except Exception as e:
        ai_error = error_handler.handle_error(
            e,
            operation="手动错误处理",
            context={"test": "data"},
            raise_exception=False
        )
        if ai_error:
            print(f"处理的错误: [{ai_error.error_code.code}] {ai_error.message}")
    
    return error_handler


def example_integration():
    """示例8: 模块集成"""
    print("\n" + "=" * 60)
    print("示例8: 模块集成")
    print("=" * 60)
    
    # 1. 初始化所有模块
    print("初始化模块...")
    memory_storage = MemoryStorage()
    mood_manager = MoodManager(storage_manager=memory_storage)
    
    # 2. 模拟对话流程
    print("\n模拟对话流程:")
    
    # 用户输入
    user_message = "我今天完成了项目，感觉很开心！"
    print(f"👤 用户: {user_message}")
    
    # 分析心情
    mood_manager.analyze_and_update(user_message)
    current_mood = mood_manager.current_mood
    print(f"🎭 AI心情: {current_mood.value} ({current_mood.emoji})")
    
    # 模拟AI回复
    ai_response = "太棒了！恭喜你完成项目，我也为你感到高兴！"
    print(f"🤖 AI: {ai_response}")
    
    # 保存对话
    conversation = {
        "user": user_message,
        "ai": ai_response,
        "mood": current_mood.value,
        "timestamp": "2024-01-01T12:00:00"
    }
    memory_storage.save_conversation(conversation)
    print("💾 对话已保存")
    
    # 获取统计
    recall = MemoryRecall(memory_storage)
    stats = recall.get_statistics()
    print(f"📊 当前对话总数: {stats.get('conversation_count', 0)}")
    
    print("\n✅ 集成示例完成")


def example_backup_restore():
    """示例9: 备份恢复"""
    print("\n" + "=" * 60)
    print("示例9: 备份恢复")
    print("=" * 60)
    
    try:
        from scripts.backup import BackupManager
        
        # 1. 创建备份管理器
        backup_manager = BackupManager()
        print("✅ 备份管理器初始化完成")
        
        # 2. 列出备份
        backups = backup_manager.list_backups()
        if backups:
            print(f"📦 现有备份 ({len(backups)} 个):")
            for backup in backups[:3]:  # 只显示前3个
                print(f"  - {backup['name']} ({backup.get('size_formatted', 'N/A')})")
        else:
            print("📭 暂无备份")
        
        # 3. 创建备份
        print("\n创建备份...")
        backup_path = backup_manager.create_backup(
            backup_name="example_backup",
            compress=True,
            include_logs=False
        )
        print(f"✅ 备份创建成功: {backup_path}")
        
        # 4. 再次列出备份
        backups = backup_manager.list_backups()
        print(f"📦 备份后数量: {len(backups)} 个")
        
    except ImportError as e:
        print(f"⚠️  备份模块不可用: {e}")
    except Exception as e:
        print(f"❌ 备份示例失败: {e}")


def example_cleanup():
    """示例10: 清理功能"""
    print("\n" + "=" * 60)
    print("示例10: 清理功能")
    print("=" * 60)
    
    try:
        from scripts.clean import CleanManager
        
        # 1. 创建清理管理器
        clean_manager = CleanManager()
        print("✅ 清理管理器初始化完成")
        
        # 2. 扫描可清理文件
        print("扫描可清理文件...")
        found_files = clean_manager.scan(dry_run=True)
        
        total_files = sum(len(files) for files in found_files.values())
        if total_files > 0:
            print(f"🔍 发现 {total_files} 个可清理文件")
            for rule_name, files in found_files.items():
                if files:
                    print(f"  {rule_name}: {len(files)} 个文件")
        else:
            print("🎉 没有发现可清理文件")
        
        # 3. 模拟清理
        print("\n模拟清理（不实际删除）...")
        results = clean_manager.clean(dry_run=True)
        
        total_deleted = sum(stats["deleted"] for stats in results.values())
        if total_deleted > 0:
            print(f"🧹 将删除 {total_deleted} 个文件")
        else:
            print("🧹 无需清理")
        
    except ImportError as e:
        print(f"⚠️  清理模块不可用: {e}")
    except Exception as e:
        print(f"❌ 清理示例失败: {e}")


@safe_call(operation="完整示例")
def main():
    """主函数 - 运行所有示例"""
    print("🚀 AI宠物MVP基础使用示例")
    print("=" * 60)
    print("本示例演示如何使用AI宠物MVP的核心模块")
    print("=" * 60)
    
    # 记录开始时间
    from src.utils.helpers import Timer
    total_timer = Timer("完整示例运行")
    
    try:
        # 运行各个示例
        example_config_management()
        example_logging_system()
        example_error_handling()
        example_mood_analysis()
        example_memory_storage()
        example_memory_search()
        example_integration()
        example_backup_restore()
        example_cleanup()
        
        # 注意：AI交互示例默认不运行，需要Ollama服务
        # 如需运行，取消下面一行的注释
        # example_ai_interaction()
        
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n\n示例运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 停止计时
        total_timer.stop()
        
        print("\n" + "=" * 60)
        print("🎉 所有示例运行完成！")
        print(f"⏱️  总运行时间: {total_timer.format_result()}")
        print("=" * 60)
        
        # 提示
        print("\n📋 下一步建议:")
        print("1. 查看生成的日志文件: logs/")
        print("2. 查看保存的数据: data/memory/")
        print("3. 查看配置文件: data/config/")
        print("4. 运行完整测试: python run_tests.py suite")
        print("5. 启动完整应用: python run_app.py")
        print("=" * 60)


if __name__ == "__main__":
    main()
    print("\n👋 示例程序结束")