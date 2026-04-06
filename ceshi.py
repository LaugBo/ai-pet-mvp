# 测试脚本 - 专门测试Ollama连接
# 功能：快速测试AI连接是否正常

import sys
import os
import json

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_ollama_connection():
    """测试Ollama连接"""
    print("=" * 60)
    print("🤖 AI宠物MVP - Ollama连接测试")
    print("=" * 60)
    
    try:
        # 导入模块
        from src.core.ai.adapter import AIManager
        
        print("✅ 模块导入成功")
        
        # 读取配置文件
        config_path = os.path.join(current_dir, "data", "config", "ai_profiles.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 获取激活的配置
        active_profile = config_data.get("active_profile", "my_ollama")
        profiles = config_data.get("profiles", {})
        
        if active_profile not in profiles:
            print(f"❌ 找不到配置: {active_profile}")
            return False
        
        profile = profiles[active_profile]
        print(f"📋 使用配置: {profile.get('name', '未知')}")
        
        # 提取配置信息
        base_url = profile.get("base_url", "http://localhost:11434")
        model = profile.get("model", "my-qwen:latest")
        
        # 解析IP和端口
        if "://" in base_url:
            address = base_url.split("://")[1]
        else:
            address = base_url
        
        if ":" in address:
            ip = address.split(":")[0]
            port = int(address.split(":")[1].split("/")[0])
        else:
            ip = address
            port = 11434
        
        print(f"🔌 连接信息:")
        print(f"   IP地址: {ip}")
        print(f"   端口: {port}")
        print(f"   模型: {model}")
        print("-" * 40)
        
        # 创建AI管理器
        ai_config = {
            "adapter_type": "ollama",
            "ip": ip,
            "port": port,
            "model": model
        }
        
        ai_manager = AIManager(ai_config)
        
        # 测试连接
        print("测试连接...")
        status = ai_manager.get_status()
        
        if status.get("available"):
            print("✅ AI连接成功!")
            print(f"   服务器地址: {status.get('address')}")
            print(f"   模型: {status.get('model')}")
            
            # 测试简单对话
            print("\n测试对话...")
            response = ai_manager.chat("你好，请用中文简单介绍一下自己")
            
            if response:
                print("✅ 对话测试成功!")
                print(f"AI回复: {response[:100]}...")
                return True
            else:
                print("❌ 对话测试失败: 未收到回复")
                return False
        else:
            print("❌ AI连接失败")
            print(f"错误信息: {status}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装依赖: pip install requests")
        return False
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        print("请检查配置文件是否存在")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("=" * 60)

def test_config_files():
    """测试配置文件"""
    print("\n📁 配置文件检查")
    print("-" * 40)
    
    config_files = [
        "settings.json",
        "ai_profiles.json", 
        "mood_rules.json"
    ]
    
    for filename in config_files:
        filepath = os.path.join(current_dir, "data", "config", filename)
        if os.path.exists(filepath):
            print(f"✅ {filename} 存在")
        else:
            print(f"❌ {filename} 不存在")

if __name__ == "__main__":
    # 测试配置文件
    test_config_files()
    
    # 测试连接
    success = test_ollama_connection()
    
    if success:
        print("\n🎉 所有测试通过！可以正常运行应用程序。")
        print("运行命令: python run_app.py")
    else:
        print("\n❌ 测试失败，请检查以上错误信息。")
    
    sys.exit(0 if success else 1)