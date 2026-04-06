# AI宠物MVP - 主程序入口文件
# 功能：程序启动入口，初始化所有组件
# 更新：支持Ollama连接

import os
import sys
import json
from src.utils.config import get_config_manager

def check_directories():
    """检查重要目录"""
    print("📁 检查项目目录结构...")
    
    directories_to_check = [
        "src",
        "src/core",
        "src/core/mood",
        "src/core/memory", 
        "src/core/ai",
        "src/ui",
        "src/utils",
        "data",
        "data/memory",
        "data/config",
        "data/memory/conversations",
        "data/memory/summaries",
        "data/memory/moods"
    ]
    
    all_exist = True
    for directory in directories_to_check:
        dir_path = os.path.join(os.path.dirname(__file__), directory)
        if os.path.exists(dir_path):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (不存在)")
            all_exist = False
    
    return all_exist

def load_configurations():
    """加载所有配置文件"""
    print("\n📄 加载配置文件...")
    
    config_mgr = get_config_manager()
    
    # 加载主要配置文件
    config_files = ["settings.json", "mood_rules.json", "ai_profiles.json"]
    
    for config_file in config_files:
        config = config_mgr.load_config(config_file, create_if_not_exist=True)
        if config:
            print(f"  ✅ {config_file} 加载成功")
            
            # 特别检查ai_profiles.json
            if config_file == "ai_profiles.json":
                active_profile = config.get("active_profile")
                profiles = config.get("profiles", {})
                if active_profile in profiles:
                    profile = profiles[active_profile]
                    print(f"     使用配置: {profile.get('name')}")
                    print(f"     模型: {profile.get('model')}")
        else:
            print(f"  ❌ {config_file} 加载失败")
    
    return config_mgr

def show_ai_info(config_mgr):
    """显示AI信息"""
    print("\n🤖 AI配置信息:")
    print("-" * 40)
    
    # 从settings.json获取
    ai_type = config_mgr.get_config_value("settings.json", "ai.adapter_type", "未知")
    default_model = config_mgr.get_config_value("settings.json", "ai.default_model", "未知")
    
    # 从ai_profiles.json获取详细信息
    ai_profiles = config_mgr.load_config("ai_profiles.json")
    active_profile = ai_profiles.get("active_profile", "my_ollama")
    profiles = ai_profiles.get("profiles", {})
    
    if active_profile in profiles:
        profile = profiles[active_profile]
        print(f"当前配置: {profile.get('name')}")
        print(f"连接地址: {profile.get('base_url')}")
        print(f"使用模型: {profile.get('model')}")
        print(f"AI类型: {ai_type}")
    else:
        print(f"使用配置: {active_profile} (未找到)")
        print(f"AI类型: {ai_type}")
        print(f"默认模型: {default_model}")

def show_system_info():
    """显示系统信息"""
    print("\n💻 系统信息:")
    print("-" * 40)
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"项目目录: {os.path.dirname(__file__)}")

def main():
    """主函数，程序从这里开始执行"""
    print("=" * 60)
    print("🚀 AI宠物MVP启动中 (Ollama版)...")
    print("=" * 60)
    
    # 1. 添加src目录到Python路径
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if src_path not in sys.path:
        sys.path.append(src_path)
    
    # 2. 检查目录结构
    if not check_directories():
        print("\n⚠️ 部分目录缺失，可能会影响功能")
        print("   建议按项目结构创建缺失的目录")
    
    # 3. 加载配置
    config_mgr = load_configurations()
    
    # 4. 显示系统信息
    show_system_info()
    
    # 5. 显示AI信息
    show_ai_info(config_mgr)
    
    # 6. 功能检查
    print("\n🔧 功能检查:")
    print("-" * 40)
    
    # 检查AI配置文件
    ai_profiles = config_mgr.get_config_value("ai_profiles.json", "profiles", {})
    if ai_profiles:
        active_profile = config_mgr.get_config_value("ai_profiles.json", "active_profile", "")
        if active_profile and active_profile in ai_profiles:
            profile = ai_profiles[active_profile]
            print(f"✅ AI配置: {profile.get('name', '未知')}")
            print(f"   地址: {profile.get('base_url', '未设置')}")
        else:
            print("❌ 未设置有效的AI配置")
    else:
        print("❌ AI配置文件为空")
    
    # 检查心情配置
    mood_rules = config_mgr.get_config_value("mood_rules.json", "moods", {})
    if mood_rules:
        print(f"✅ 心情系统: 已配置 {len(mood_rules)} 种心情")
    else:
        print("❌ 心情配置文件为空")
    
    print("\n" + "=" * 60)
    print("✅ 配置加载完成")
    print("✅ 程序骨架就绪，可以开始功能开发")
    print("=" * 60)
    print("💡 运行应用程序: python run_app.py")
    print("💡 测试连接: python ceshi.py")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    # 运行主函数
    exit_code = main()
    sys.exit(exit_code)