@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 AI宠物MVP快速启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)

echo ✅ 虚拟环境已激活

REM 检查依赖
echo.
echo 📦 检查依赖...
if not exist "requirements.txt" (
    echo ❌ 依赖文件不存在
    pause
    exit /b 1
)

REM 安装依赖
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖检查完成

REM 运行测试
echo.
echo 🔧 运行连接测试...
python ceshi.py
if errorlevel 1 (
    echo.
    echo ❌ 连接测试失败
    echo 请检查AI服务器是否运行
    pause
    exit /b 1
)

echo.
echo ✅ 所有测试通过！
echo.

REM 启动应用程序
echo 🎮 启动应用程序...
echo 按 Ctrl+C 可关闭程序
echo ========================================
python run_app.py

pause