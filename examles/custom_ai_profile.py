#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义AI配置示例
展示如何创建和使用自定义AI配置
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.ai.adapter import AIManager, AIAdapter
from src.utils.config import get_config_manager
from src.utils.logger import get_logger, info
from src.utils.helpers import Timer, safe_execute
from src.utils.error_handler import safe_call


def example_create_custom_config():
    """示例1: 创建自定义配置"""
    print("=" * 60)
    print("示例1: 创建自定义AI配置")
    print("=" * 60)
    
    # 1. 获取配置管理器
    config_manager = get_config_manager()
    
    # 2. 创建自定义AI配置
    custom_ai_config = {
        "active_profile": "my_custom_ai",
        "profiles": {
            "my_custom_ai": {
                "name": "我的自定义AI",
                "type": "ollama",  # 支持: ollama, openai, claude, etc.
                "base_url": "http://localhost:11434",  # Ollama默认地址
                "model": "qwen:7b",  # 使用的模型
                "timeout": 60,  # 超时时间(秒)
                "temperature": 0.7,  # 创造性参数
                "max_tokens": 2048,  # 最大生成长度
                "stream": False  # 是否流式输出
            },
            "openai_config": {
                "name": "OpenAI GPT-4",
                "type": "openai",
                "api_key": "${OPENAI_API_KEY}",  # 从环境变量读取
                "model": "gpt-4",
                "base_url": "https://api.openai.com/v1",
                "timeout": 30
            },
            "claude_config": {
                "name": "Anthropic Claude",
                "type": "claude",
                "api_key": "${ANTHROPIC_API_KEY}",
                "model": "claude-3-sonnet-20240229",
                "base_url": "https://api.anthropic.com",
                "timeout": 30
            }
        }
    }
    
    # 3. 保存配置
    result = config_manager.save_config("custom_ai_profiles.json", custom_ai_config)
    if result:
        print("✅ 自定义AI配置已保存")
        print(f"   位置: {config_manager.get_config_path('custom_ai_profiles.json')}")
    else:
        print("❌ 保存配置失败")
        return None
    
    return config_manager


def example_load_custom_config():
    """示例2: 加载自定义配置"""
    print("\n" + "=" * 60)
    print("示例2: 加载自定义配置")
    print("=" * 60)
    
    # 1. 获取配置管理器
    config_manager = get_config_manager()
    
    # 2. 加载配置
    config = config_manager.load_config("custom_ai_profiles.json")
    if not config:
        print("⚠️  未找到自定义配置，使用默认配置")
        config = config_manager.load_config("ai_profiles.json")
    
    if config:
        print("✅ 配置加载成功")
        
        # 3. 显示配置信息
        active_profile = config.get("active_profile", "default")
        profiles = config.get("profiles", {})
        
        print(f"   激活配置: {active_profile}")
        print(f"   可用配置数量: {len(profiles)}")
        
        for profile_id, profile in profiles.items():
            print(f"\n   📋 配置: {profile.get('name', profile_id)}")
            print(f"     类型: {profile.get('type', 'unknown')}")
            print(f"     模型: {profile.get('model', 'N/A')}")
            if profile.get("base_url"):
                print(f"     地址: {profile.get('base_url')}")
    
    return config


def example_create_custom_adapter():
    """示例3: 创建自定义适配器"""
    print("\n" + "=" * 60)
    print("示例3: 创建自定义适配器")
    print("=" * 60)
    
    # 1. 自定义AI适配器（模拟示例）
    class CustomAIAdapter(AIAdapter):
        """自定义AI适配器示例"""
        
        def __init__(self, config: Dict[str, Any]):
            self.config = config
            self.name = config.get("name", "自定义AI")
            self.model = config.get("model", "custom-model")
            self._is_connected = False
            self.api_key = config.get("api_key")
            
            print(f"🔧 创建自定义适配器: {self.name}")
            print(f"   模型: {self.model}")
        
        @property
        def ai_type(self) -> str:
            return "custom"
        
        @property
        def is_connected(self) -> bool:
            return self._is_connected
        
        def connect(self) -> bool:
            """模拟连接AI服务"""
            print("🔌 连接自定义AI服务...")
            
            # 模拟连接过程
            if self.api_key == "invalid":
                print("❌ 连接失败: API密钥无效")
                return False
            
            self._is_connected = True
            print("✅ 自定义AI连接成功")
            return True
        
        def disconnect(self):
            """断开连接"""
            print("🔌 断开自定义AI连接")
            self._is_connected = False
        
        def generate(self, prompt: str, **kwargs) -> str:
            """生成响应"""
            if not self._is_connected:
                return "错误: AI未连接"
            
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 100)
            
            print(f"💬 生成响应 (温度: {temperature}, 长度: {max_tokens})")
            print(f"   提示: {prompt[:50]}...")
            
            # 模拟AI响应
            response = f"""
[来自 {self.name} 的回复]
模型: {self.model}
温度: {temperature}

{prompt}

这是我根据你的输入生成的回复。这是一个示例回复，实际使用时会调用真正的AI服务。

这是自定义适配器的演示，你可以根据需要实现真实的AI服务调用。
"""
            
            return response
    
    # 2. 创建并测试适配器
    custom_config = {
        "name": "我的自定义AI",
        "model": "custom-model-v1",
        "api_key": "valid-key-123"
    }
    
    adapter = CustomAIAdapter(custom_config)
    
    # 测试连接
    if adapter.connect():
        # 测试生成
        with Timer("自定义适配器响应"):
            response = adapter.generate("你好，请介绍一下你自己", temperature=0.8)
            print(f"\n🤖 响应:\n{response[:200]}...")
        
        # 断开连接
        adapter.disconnect()
    
    return adapter


def example_switch_ai_profiles():
    """示例4: 动态切换AI配置"""
    print("\n" + "=" * 60)
    print("示例4: 动态切换AI配置")
    print("=" * 60)
    
    # 1. 创建多个AI配置
    ai_configs = {
        "fast_model": {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "tinyllama:latest",  # 小型快速模型
            "timeout": 10
        },
        "smart_model": {
            "adapter_type": "ollama",
            "ip": "localhost", 
            "port": 11434,
            "model": "qwen:14b",  # 大型智能模型
            "timeout": 60
        },
        "creative_model": {
            "adapter_type": "ollama",
            "ip": "localhost",
            "port": 11434,
            "model": "mistral:7b",  # 创造性模型
            "temperature": 0.9,
            "timeout": 30
        }
    }
    
    # 2. 创建AI管理器列表
    ai_managers = {}
    
    for config_name, config in ai_configs.items():
        print(f"\n🔧 创建AI管理器: {config_name}")
        print(f"   模型: {config.get('model')}")
        
        # 创建AI管理器
        try:
            ai_manager = AIManager(config)
            ai_managers[config_name] = ai_manager
            print("✅ 创建成功")
        except Exception as e:
            print(f"❌ 创建失败: {e}")
    
    # 3. 演示切换（模拟）
    print("\n🔄 AI配置切换演示:")
    
    test_prompt = "用一句话介绍你自己"
    
    for config_name, ai_manager in ai_managers.items():
        print(f"\n使用 {config_name}:")
        print(f"  模型: {ai_manager.config.get('model')}")
        
        # 在实际使用时，这里会调用 connect() 和 generate_response()
        # 由于是演示，我们只显示配置信息
    
    return ai_managers


def example_environment_variables():
    """示例5: 使用环境变量配置"""
    print("\n" + "=" * 60)
    print("示例5: 使用环境变量配置")
    print("=" * 60)
    
    import os
    
    # 1. 设置环境变量（模拟）
    os.environ["OPENAI_API_KEY"] = "sk-example123"
    os.environ["AI_MODEL"] = "gpt-4"
    os.environ["AI_TIMEOUT"] = "30"
    
    # 2. 从环境变量创建配置
    ai_config = {
        "adapter_type": "openai",
        "api_key": os.getenv("OPENAI_API_KEY", "default-key"),
        "model": os.getenv("AI_MODEL", "gpt-3.5-turbo"),
        "timeout": int(os.getenv("AI_TIMEOUT", "60"))
    }
    
    print("🔧 从环境变量创建的配置:")
    for key, value in ai_config.items():
        print(f"   {key}: {value}")
    
    # 3. 使用配置文件模板
    config_template = {
        "ai": {
            "api_key": "${OPENAI_API_KEY}",
            "model": "${AI_MODEL:-gpt-3.5-turbo}",  # 默认值
            "timeout": "${AI_TIMEOUT:-60}"
        }
    }
    
    print("\n📄 配置文件模板（支持环境变量）:")
    print(json.dumps(config_template, indent=2, ensure_ascii=False))
    
    return ai_config


def example_validate_config():
    """示例6: 配置验证"""
    print("\n" + "=" * 60)
    print("示例6: 配置验证")
    print("=" * 60)
    
    def validate_ai_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """验证AI配置"""
        errors = []
        
        # 检查必需字段
        required_fields = ["adapter_type", "model"]
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查适配器类型
        adapter_type = config.get("adapter_type")
        if adapter_type not in ["ollama", "openai", "claude"]:
            errors.append(f"不支持的适配器类型: {adapter_type}")
        
        # 检查Ollama配置
        if adapter_type == "ollama":
            if "ip" not in config:
                errors.append("Ollama配置需要ip字段")
            if "port" not in config:
                errors.append("Ollama配置需要port字段")
        
        # 检查OpenAI配置
        elif adapter_type == "openai":
            if "api_key" not in config:
                errors.append("OpenAI配置需要api_key字段")
        
        # 检查超时时间
        timeout = config.get("timeout", 60)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("timeout必须是正数")
        
        if errors:
            return False, "; ".join(errors)
        return True, "配置有效"
    
    # 测试不同配置
    test_configs = [
        {
            "name": "有效Ollama配置",
            "config": {
                "adapter_type": "ollama",
                "ip": "localhost",
                "port": 11434,
                "model": "qwen:7b",
                "timeout": 60
            }
        },
        {
            "name": "无效配置（缺少字段）",
            "config": {
                "adapter_type": "ollama",
                "model": "test"
                # 缺少ip和port
            }
        },
        {
            "name": "无效配置（错误类型）",
            "config": {
                "adapter_type": "unknown",  # 未知类型
                "model": "test"
            }
        },
        {
            "name": "有效OpenAI配置",
            "config": {
                "adapter_type": "openai",
                "api_key": "sk-123",
                "model": "gpt-4"
            }
        }
    ]
    
    for test in test_configs:
        print(f"\n🔍 验证: {test['name']}")
        is_valid, message = validate_ai_config(test["config"])
        
        if is_valid:
            print("✅ 验证通过")
        else:
            print(f"❌ 验证失败: {message}")
    
    return validate_ai_config


def example_backup_restore_config():
    """示例7: 备份和恢复配置"""
    print("\n" + "=" * 60)
    print("示例7: 备份和恢复配置")
    print("=" * 60)
    
    config_manager = get_config_manager()
    
    # 1. 创建测试配置
    test_config = {
        "version": "1.0.0",
        "created_at": "2024-01-01T00:00:00",
        "ai": {
            "active_model": "test-model",
            "temperature": 0.7
        }
    }
    
    # 2. 保存配置
    config_file = "test_backup_config.json"
    config_manager.save_config(config_file, test_config)
    print(f"✅ 测试配置已保存: {config_file}")
    
    # 3. 备份配置
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    import shutil
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"config_backup_{timestamp}.json"
    
    config_path = config_manager.get_config_path(config_file)
    shutil.copy2(config_path, backup_file)
    
    print(f"✅ 配置已备份: {backup_file}")
    
    # 4. 模拟配置损坏
    print("\n🔧 模拟配置损坏...")
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write("损坏的配置内容")
    
    # 5. 从备份恢复
    print("🔄 从备份恢复配置...")
    shutil.copy2(backup_file, config_path)
    print(f"✅ 配置已从备份恢复")
    
    # 6. 验证恢复
    restored = config_manager.load_config(config_file)
    if restored == test_config:
        print("✅ 恢复验证成功: 配置完整恢复")
    else:
        print("❌ 恢复验证失败")
    
    # 7. 清理
    os.remove(config_path)
    os.remove(backup_file)
    print("🧹 测试文件已清理")
    
    return backup_file


def example_advanced_config_features():
    """示例8: 高级配置功能"""
    print("\n" + "=" * 60)
    print("示例8: 高级配置功能")
    print("=" * 60)
    
    # 1. 配置继承
    base_config = {
        "common": {
            "timeout": 60,
            "retry_count": 3,
            "language": "zh-CN"
        }
    }
    
    model_configs = {
        "fast": {**base_config, "model": "tinyllama", "temperature": 0.3},
        "balanced": {**base_config, "model": "qwen:7b", "temperature": 0.7},
        "creative": {**base_config, "model": "mistral", "temperature": 0.9}
    }
    
    print("🔧 配置继承示例:")
    for name, config in model_configs.items():
        print(f"\n   {name}配置:")
        print(f"     模型: {config.get('model')}")
        print(f"     温度: {config.get('temperature')}")
        print(f"     超时: {config.get('common', {}).get('timeout')}")
    
    # 2. 动态配置
    def create_dynamic_config(use_case: str) -> Dict[str, Any]:
        """根据用例创建动态配置"""
        config_templates = {
            "chat": {
                "temperature": 0.7,
                "max_tokens": 1000,
                "system_prompt": "你是一个友好的助手"
            },
            "code": {
                "temperature": 0.2,
                "max_tokens": 2000,
                "system_prompt": "你是一个编程助手"
            },
            "creative": {
                "temperature": 0.9,
                "max_tokens": 500,
                "system_prompt": "你是一个创意写手"
            }
        }
        
        template = config_templates.get(use_case, config_templates["chat"])
        return {
            "adapter_type": "ollama",
            "model": "qwen:7b",
            **template
        }
    
    print("\n🔧 动态配置示例:")
    for use_case in ["chat", "code", "creative"]:
        config = create_dynamic_config(use_case)
        print(f"\n   {use_case}用例:")
        print(f"     温度: {config.get('temperature')}")
        print(f"     系统提示: {config.get('system_prompt', 'N/A')}")
    
    # 3. 配置验证规则
    validation_rules = {
        "temperature": {"type": float, "min": 0.0, "max": 2.0},
        "max_tokens": {"type": int, "min": 1, "max": 8192},
        "timeout": {"type": int, "min": 1, "max": 300},
        "model": {"type": str, "required": True}
    }
    
    print("\n🔧 配置验证规则:")
    for field, rules in validation_rules.items():
        print(f"   {field}: {rules}")
    
    return model_configs


@safe_call(operation="自定义AI配置示例")
def main():
    """主函数 - 运行所有示例"""
    print("🚀 AI宠物MVP - 自定义AI配置示例")
    print("=" * 60)
    print("本示例演示如何创建、管理和使用自定义AI配置")
    print("=" * 60)
    
    # 记录开始时间
    from src.utils.helpers import Timer
    total_timer = Timer("完整示例运行")
    
    try:
        # 运行各个示例
        example_create_custom_config()
        example_load_custom_config()
        example_create_custom_adapter()
        example_switch_ai_profiles()
        example_environment_variables()
        example_validate_config()
        example_backup_restore_config()
        example_advanced_config_features()
        
        print("\n" + "=" * 60)
        print("🎉 自定义配置示例完成！")
        print("=" * 60)
        
        # 总结
        print("\n📋 关键要点总结:")
        print("1. ✅ 可以创建自定义AI配置文件")
        print("2. ✅ 支持多种AI服务 (Ollama, OpenAI, Claude)")
        print("3. ✅ 支持环境变量配置")
        print("4. ✅ 支持配置验证和备份")
        print("5. ✅ 支持动态配置和配置继承")
        
        print("\n🔧 实际应用建议:")
        print("1. 在 data/config/ 中创建自定义配置")
        print("2. 使用环境变量管理敏感信息（如API密钥）")
        print("3. 定期备份重要配置")
        print("4. 为不同用例创建不同配置模板")
        
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