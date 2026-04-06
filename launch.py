# AI宠物MVP - 启动脚本
# 功能：提供便捷启动方式，处理启动前准备工作
# 更新：支持Ollama版启动

import subprocess
import sys
import os

def check_venv():
    """检查虚拟环境是否激活"""
    print("🔍 检查Python环境...")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境已激活")
        return True
    else:
        print("⚠️ 不在虚拟环境中，尝试激活...")
        
        # 尝试自动激活
        venv_path = os.path.join(os.path.dirname(__file__), "venv")
        if os.path.exists(venv_path):
            print(f"虚拟环境路径: {venv_path}")
            return True
        else:
            print("❌ 未找到虚拟环境，请先创建: python -m venv venv")
            return False

def check_requirements():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if os.path.exists(req_file):
        print(f"✅ 找到 requirements.txt")
        
        # 检查关键依赖
        try:
            import PyQt5
            import requests
            print("✅ 关键依赖已安装: PyQt5, requests")
            return True
        except ImportError as e:
            print(f"⚠️ 依赖缺失: {e}")
            print("正在安装依赖...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
                print("✅ 依赖安装完成")
                return True
            except subprocess.CalledProcessError:
                print("❌ 依赖安装失败")
                return False
    else:
        print("⚠️ 未找到 requirements.txt，将创建空文件")
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("# AI宠物MVP依赖包\n")
        return True

def start_program():
    """启动主程序"""
    print("\n" + "=" * 50)
    print("🚀 启动AI宠物MVP (Ollama版)...")
    print("=" * 50)
    
    try:
        # 先运行配置检查
        print("运行配置检查...")
        check_result = subprocess.run(
            [sys.executable, "ceshi.py"],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        print(check_result.stdout)
        
        if check_result.returncode != 0:
            print("❌ 配置检查失败")
            print("请先解决上述问题，再启动应用程序")
            return 1
        
        # 运行主程序
        result = subprocess.run(
            [sys.executable, "run_app.py"], 
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        print(result.stdout)
        if result.stderr:
            print("标准错误:", result.stderr)
        
        return result.returncode
        
    except Exception as e:
        print(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    print("🚀 AI宠物MVP启动器 (Ollama版)")
    print("-" * 30)
    
    # 1. 检查环境
    if not check_venv():
        print("\n请先激活虚拟环境:")
        print("Windows: venv\\Scripts\\activate")
        print("Mac/Linux: source venv/bin/activate")
        sys.exit(1)
    
    # 2. 检查依赖
    if not check_requirements():
        print("\n请手动安装依赖:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # 3. 启动程序
    exit_code = start_program()
    sys.exit(exit_code)