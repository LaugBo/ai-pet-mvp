#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
功能：启动完整的应用程序
更新：集成所有系统模块
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def setup_environment():
    """设置环境"""
    # 设置编码
    if sys.platform == "win32":
        import _locale
        _locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])
    
    # 设置工作目录
    os.chdir(current_dir)
    
    return current_dir

def main():
    """主函数"""
    try:
        # 0. 设置环境
        project_dir = setup_environment()
        
        # 1. 初始化日志系统（必须在最前面）
        from src.utils.logger import setup_logging, get_logger, exception
        from src.utils.error_handler import setup_global_exception_handler
        
        logger = setup_logging("ai_pet", "INFO")
        error_handler = setup_global_exception_handler(logger)
        
        logger.info("=" * 60)
        logger.info("🚀 启动AI宠物MVP完整应用程序")
        logger.info("=" * 60)
        
        # 2. 记录系统信息
        logger.log_system_info()
        
        # 3. 导入所有必要模块
        try:
            from src.ui.window import MainWindow
            from src.ui.chat import ChatManager
            from src.utils.config import get_config_manager
            from src.core.ai.adapter import AIManager
            from src.core.memory.storage import MemoryStorage
            from src.core.mood.manager import MoodManager
            from src.core.mood.images import MoodImageManager
            
            logger.info("✅ 模块导入成功")
        except ImportError as e:
            logger.critical(f"❌ 模块导入失败: {e}")
            logger.error("请确保已安装所有依赖: pip install -r requirements.txt")
            return 1
        
        # 4. 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("AI宠物MVP")
        app.setStyle("Fusion")
        
        logger.info("✅ 创建Qt应用")
        
        # 5. 加载配置
        try:
            config_manager = get_config_manager()
            logger.info("✅ 加载配置管理器")
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 使用默认配置继续
            config_manager = None
        
        # 6. 从配置文件读取AI设置
        logger.info("读取AI配置...")
        ai_config = {}
        
        if config_manager:
            try:
                ai_profiles = config_manager.load_config("ai_profiles.json")
                active_profile = ai_profiles.get("active_profile", "my_ollama")
                profiles = ai_profiles.get("profiles", {})
                
                if active_profile in profiles:
                    profile = profiles[active_profile]
                    logger.info(f"✅ 使用AI配置: {profile.get('name')}")
                    
                    # 构建AI配置
                    base_url = profile.get("base_url", "http://localhost:11434")
                    if "://" in base_url:
                        address = base_url.split("://")[1]
                        ip = address.split(":")[0]
                        port = int(address.split(":")[1].split("/")[0])
                    else:
                        ip = base_url
                        port = 11434
                    
                    ai_config = {
                        "adapter_type": profile.get("type", "ollama"),
                        "ip": ip,
                        "port": port,
                        "model": profile.get("model", "my-qwen:latest"),
                        "timeout": profile.get("timeout", 60)
                    }
                    
                    logger.info(f"   IP: {ai_config['ip']}")
                    logger.info(f"   端口: {ai_config['port']}")
                    logger.info(f"   模型: {ai_config['model']}")
                    
                else:
                    logger.warning("⚠️ 使用默认AI配置")
                    ai_config = {
                        "adapter_type": "ollama",
                        "ip": "localhost",
                        "port": 11434,
                        "model": "my-qwen:latest"
                    }
                    
            except Exception as e:
                logger.warning(f"读取AI配置失败，使用默认配置: {e}")
                ai_config = {
                    "adapter_type": "ollama",
                    "ip": "localhost",
                    "port": 11434,
                    "model": "my-qwen:latest"
                }
        else:
            logger.warning("⚠️ 无配置管理器，使用硬编码AI配置")
            ai_config = {
                "adapter_type": "ollama",
                "ip": "localhost",
                "port": 11434,
                "model": "my-qwen:latest"
            }
        
        # 7. 创建AI管理器
        logger.info("创建AI管理器...")
        try:
            ai_manager = AIManager(ai_config)
            logger.info("✅ AI管理器创建完成")
        except Exception as e:
            logger.error(f"AI管理器创建失败: {e}")
            # 创建基础AI管理器
            ai_manager = None
        
        # 8. 创建记忆存储系统
        logger.info("创建记忆存储系统...")
        try:
            memory_storage = MemoryStorage()
            logger.info("✅ 记忆存储系统创建完成")
        except Exception as e:
            logger.error(f"记忆系统创建失败: {e}")
            memory_storage = None
        
        # 9. 创建心情系统
        logger.info("创建心情系统...")
        
        mood_image_manager = None
        mood_manager = None
        
        try:
            # 9.1 创建心情图片管理器
            mood_image_manager = MoodImageManager()
            logger.info("✅ 心情图片管理器创建完成")
            
            # 9.2 创建心情管理器
            mood_manager = MoodManager(storage_manager=memory_storage)
            logger.info("✅ 心情管理器创建完成")
            
            # 9.3 注册心情变化回调
            def on_mood_change(old_mood, new_result):
                logger.info(f"🎭 心情变化: {old_mood.value} -> {new_result.mood_type.value}")
                logger.info(f"   原因: {new_result.reason}")
                logger.info(f"   置信度: {new_result.confidence:.1%}")
            
            mood_manager.register_mood_change_callback(on_mood_change)
            logger.info("✅ 心情回调注册完成")
            
        except Exception as e:
            logger.error(f"心情系统创建失败: {e}")
        
        # 10. 创建聊天管理器
        logger.info("创建聊天管理器...")
        try:
            chat_manager = ChatManager(config_manager, ai_manager)
            logger.info("✅ 聊天管理器创建完成")
        except Exception as e:
            logger.error(f"聊天管理器创建失败: {e}")
            chat_manager = None
        
        # 11. 创建主窗口
        logger.info("创建主窗口...")
        try:
            window = MainWindow(config_manager, mood_manager, mood_image_manager)
            logger.info("✅ 主窗口创建完成")
        except Exception as e:
            logger.critical(f"主窗口创建失败: {e}")
            raise
        
        # 12. 连接信号
        logger.info("连接信号...")
        try:
            _connect_signals(window, chat_manager, ai_manager)
        except Exception as e:
            logger.error(f"信号连接失败: {e}")
        
        # 13. 显示窗口
        window.show()
        logger.info("✅ 窗口显示完成")
        
        # 14. 异步连接AI
        logger.info("异步连接AI...")
        if chat_manager and ai_manager:
            QTimer.singleShot(1000, lambda: _try_connect_ai(chat_manager, window, logger))
        else:
            logger.warning("跳过AI连接（聊天管理器或AI管理器不可用）")
        
        # 15. 显示启动信息
        logger.info("=" * 60)
        logger.info("🎉 应用程序启动完成！")
        logger.info("📝 功能说明:")
        logger.info("   1. 左侧: 聊天对话区域")
        logger.info("   2. 右侧: AI宠物心情显示")
        logger.info("   3. 输入消息，点击发送或按 Ctrl+Enter")
        logger.info("   4. 心情会根据对话内容变化")
        logger.info("   5. 所有对话自动保存")
        logger.info("=" * 60)
        logger.info("💡 提示: AI连接可能需要几秒钟时间")
        logger.info("=" * 60)
        
        # 16. 注册应用关闭处理
        def on_app_exit():
            logger.info("🛑 应用程序正在关闭...")
            
            # 清理资源
            if chat_manager:
                chat_manager.disconnect()
            
            if mood_manager:
                mood_manager.save_current_mood()
            
            logger.info("✅ 应用程序已安全关闭")
            logger.info("=" * 60)
        
        app.aboutToQuit.connect(on_app_exit)
        
        # 17. 运行应用
        return_code = app.exec_()
        
        logger.info(f"应用程序退出，返回码: {return_code}")
        return return_code
        
    except KeyboardInterrupt:
        logger.info("应用程序被用户中断")
        return 130
        
    except Exception as e:
        # 记录未捕获的异常
        exception(f"应用程序启动失败: {e}")
        error_msg = traceback.format_exc()
        logger.critical(f"致命错误:\n{error_msg}")
        
        # 尝试显示错误对话框
        try:
            error_app = QApplication([])
            from PyQt5.QtWidgets import QMessageBox
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("应用程序启动失败")
            msg_box.setText(f"应用程序启动时发生错误:\n\n{str(e)[:200]}")
            msg_box.setDetailedText(error_msg)
            msg_box.exec_()
        except:
            pass
        
        return 1

def _connect_signals(window, chat_manager, ai_manager):
    """连接所有信号"""
    if not chat_manager or not ai_manager:
        return
    
    # 窗口消息 -> 聊天管理器
    window.send_message_signal.connect(chat_manager.send_message)
    
    # 聊天管理器 -> 窗口更新
    chat_manager.response_received.connect(window.update_ai_response)
    chat_manager.error_occurred.connect(window.show_error)
    chat_manager.status_changed.connect(window.update_connection_status)
    
    # 窗口关闭 -> 清理
    window.close_window_signal.connect(chat_manager.disconnect)
    
    print("✅ 信号连接完成")

def _try_connect_ai(chat_manager, window, logger):
    """尝试连接AI"""
    logger.info("尝试连接AI...")
    
    # 更新连接状态
    window.update_connection_status("正在连接...", False)
    
    # 尝试连接
    try:
        if chat_manager.connect_ai():
            window.update_connection_status("已连接", True)
            
            # 显示欢迎消息
            welcome_msg = "AI宠物已连接！你可以开始对话了。"
            window._add_system_message(welcome_msg)
            
            # 显示心情系统就绪
            window._add_system_message("心情系统已就绪，AI宠物的心情会根据对话内容变化")
            
            logger.info("✅ AI连接成功")
        else:
            window.update_connection_status("连接失败", False)
            error_msg = "无法连接到AI服务器。请检查：\n1. Ollama服务是否运行\n2. IP地址是否正确\n3. 网络连接"
            window.show_error(error_msg)
            logger.error("❌ AI连接失败")
    except Exception as e:
        logger.error(f"AI连接异常: {e}")
        window.update_connection_status("连接异常", False)
        window.show_error(f"连接过程中发生异常: {str(e)}")

if __name__ == "__main__":
    sys.exit(main())