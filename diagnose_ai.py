# AI连接诊断脚本
import sys
import os
import requests
import json

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_direct_connection():
    """直接测试Ollama连接"""
    print("=" * 60)
    print("🔍 AI连接诊断")
    print("=" * 60)
    
    # 1. 测试配置
    print("\n1. 检查配置文件...")
    config_path = os.path.join(current_dir, "data", "config", "ai_profiles.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        active_profile = config.get("active_profile", "my_ollama")
        profiles = config.get("profiles", {})
        
        if active_profile in profiles:
            profile = profiles[active_profile]
            print(f"✅ 使用配置: {profile.get('name')}")
            print(f"   地址: {profile.get('base_url')}")
            print(f"   模型: {profile.get('model')}")
            
            # 提取IP和端口
            base_url = profile.get("base_url", "http://192.168.1.13:11434")
            return base_url, profile.get("model")
        else:
            print(f"❌ 配置 '{active_profile}' 不存在")
    else:
        print(f"❌ 配置文件不存在: {config_path}")
    
    return None, None

def test_ollama_connection(base_url, model):
    """测试Ollama连接"""
    print("\n2. 测试Ollama连接...")
    
    try:
        # 测试基础连接
        print(f"   测试连接: {base_url}")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 基础连接成功")
            
            # 测试版本接口
            print(f"   测试版本接口...")
            version_url = f"{base_url}/api/version"
            response = requests.get(version_url, timeout=5)
            
            if response.status_code == 200:
                version_info = response.json()
                print(f"   ✅ Ollama版本: {version_info.get('version', '未知')}")
            else:
                print(f"   ❌ 版本接口失败: {response.status_code}")
                
            # 测试模型接口
            print(f"   检查模型 '{model}'...")
            tags_url = f"{base_url}/api/tags"
            response = requests.get(tags_url, timeout=5)
            
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get("models", [])
                model_names = [m.get("name") for m in models]
                print(f"   ✅ 可用模型: {model_names}")
                
                if model in model_names:
                    print(f"   ✅ 模型 '{model}' 可用")
                else:
                    print(f"   ❌ 模型 '{model}' 不存在")
                    print(f"     请用 'ollama list' 查看可用模型")
                    
            else:
                print(f"   ❌ 模型接口失败: {response.status_code}")
                
        else:
            print(f"   ❌ 基础连接失败")
            print(f"     请检查Ollama服务是否运行")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接被拒绝")
        print(f"     可能原因:")
        print(f"     1. Ollama服务未启动 (运行 'ollama serve')")
        print(f"     2. IP地址错误")
        print(f"     3. 防火墙阻止")
    except requests.exceptions.Timeout:
        print(f"   ❌ 连接超时")
        print(f"     网络可能较慢，或Ollama无响应")
    except Exception as e:
        print(f"   ❌ 连接异常: {e}")

def test_project_modules():
    """测试项目模块"""
    print("\n3. 测试项目模块...")
    
    try:
        from src.core.ai.adapter import AIManager
        print("   ✅ AI管理器导入成功")
        
        # 测试创建AI管理器
        config = {
            "adapter_type": "ollama",
            "ip": "192.168.1.13",
            "port": 11434,
            "model": "my-qwen:latest"
        }
        
        ai = AIManager(config)
        print("   ✅ AI管理器创建成功")
        
        status = ai.get_status()
        print(f"   AI状态: {status}")
        
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
    except Exception as e:
        print(f"   ❌ 模块异常: {e}")

def check_network():
    """检查网络连接"""
    print("\n4. 网络检查...")
    
    import socket
    
    # 检查是否能ping通主机
    host = "192.168.1.13"
    port = 11434
    
    print(f"   测试连接到 {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"   ✅ 端口 {port} 可连接")
        else:
            print(f"   ❌ 端口 {port} 不可连接")
            print(f"      错误码: {result}")
            print(f"      可能原因:")
            print(f"      1. 主机未开机")
            print(f"      2. Ollama未运行")
            print(f"      3. 防火墙阻止")
            
        sock.close()
        
    except Exception as e:
        print(f"   ❌ 网络测试异常: {e}")

def main():
    """主诊断函数"""
    # 获取配置
    base_url, model = test_direct_connection()
    
    if base_url and model:
        # 测试Ollama连接
        test_ollama_connection(base_url, model)
    
    # 测试网络
    check_network()
    
    # 测试模块
    test_project_modules()
    
    print("\n" + "=" * 60)
    print("🔧 解决方案建议")
    print("=" * 60)
    print("\n如果AI离线，请按以下步骤解决:")
    print("\n1. 在AI主机上运行:")
    print("   ollama serve")
    print("\n2. 检查IP地址是否正确:")
    print("   在AI主机运行: ipconfig (Windows) 或 ifconfig (Mac/Linux)")
    print("   查看局域网IP地址")
    print("\n3. 检查模型是否存在:")
    print("   ollama list")
    print("\n4. 测试直接连接:")
    print("   curl http://192.168.1.13:11434/")
    print("\n5. 修改配置文件:")
    print("   编辑 data/config/ai_profiles.json")
    print("   确保 IP、端口、模型名正确")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()