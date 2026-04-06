#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI窗口模块测试
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest

from src.ui.window import MainWindow
from src.ui.chat import ChatManager
from src.core.mood.manager import MoodManager, MoodType
from src.core.mood.images import MoodImageManager


class TestMainWindow:
    """主窗口测试"""
    
    @pytest.fixture
    def app(self):
        """Qt应用fixture"""
        app = QApplication.instance() or QApplication([])
        yield app
    
    @pytest.fixture
    def mock_components(self):
        """模拟组件fixture"""
        # 模拟配置管理器
        config_manager = Mock()
        config_manager.load_config.return_value = {}
        
        # 模拟心情管理器
        mood_manager = Mock()
        mood_manager.current_mood = MoodType.HAPPY
        mood_manager.analyze_and_update = Mock(return_value=True)
        
        # 模拟图片管理器
        image_manager = Mock()
        image_manager.get_mood_image_path.return_value = "/fake/path/happy.png"
        
        return config_manager, mood_manager, image_manager
    
    def test_initialization(self, app, mock_components):
        """测试窗口初始化"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        assert window.config_manager == config_manager
        assert window.mood_manager == mood_manager
        assert window.mood_image_manager == image_manager
        assert window.chat_manager is None
        assert window.ai_manager is None
        
        # 检查UI组件
        assert window.chat_input is not None
        assert window.send_button is not None
        assert window.chat_display is not None
        assert window.mood_label is not None
        
        window.close()
    
    def test_setup_ui(self, app, mock_components):
        """测试UI设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 检查窗口属性
        assert window.windowTitle() == "AI宠物MVP"
        assert window.minimumWidth() > 0
        assert window.minimumHeight() > 0
        
        # 检查布局
        assert window.central_widget is not None
        assert window.main_layout is not None
        
        window.close()
    
    def test_setup_chat_area(self, app, mock_components):
        """测试聊天区域设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 检查聊天区域组件
        assert window.chat_display is not None
        assert window.chat_input is not None
        assert window.send_button is not None
        
        # 检查发送按钮文本
        assert window.send_button.text() == "发送"
        
        # 检查输入框占位符
        assert window.chat_input.placeholderText() == "输入消息..."
        
        window.close()
    
    def test_setup_mood_area(self, app, mock_components):
        """测试心情区域设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 检查心情区域组件
        assert window.mood_label is not None
        assert window.mood_status is not None
        assert window.mood_reason is not None
        
        # 初始应该显示"加载中..."
        assert window.mood_status.text() == "心情: 加载中..."
        
        window.close()
    
    def test_setup_signals(self, app, mock_components):
        """测试信号设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 检查发送按钮点击信号
        assert window.send_button.clicked is not None
        
        # 检查输入框回车信号
        assert window.chat_input.returnPressed is not None
        
        window.close()
    
    def test_update_mood_display_happy(self, app, mock_components):
        """测试更新心情显示（开心）"""
        config_manager, mood_manager, image_manager = mock_components
        
        # 模拟图片路径
        image_manager.get_mood_image_path.return_value = "/fake/path/happy.png"
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 更新心情显示
        window._update_mood_display(
            mood_type=MoodType.HAPPY,
            confidence=0.85,
            reason="用户说了开心的话"
        )
        
        # 检查心情状态
        assert "开心" in window.mood_status.text()
        assert "85%" in window.mood_status.text()
        
        # 检查原因
        assert window.mood_reason.text() == "原因: 用户说了开心的话"
        
        # 应该调用图片管理器
        image_manager.get_mood_image_path.assert_called_with("happy")
        
        window.close()
    
    def test_update_mood_display_sad(self, app, mock_components):
        """测试更新心情显示（伤心）"""
        config_manager, mood_manager, image_manager = mock_components
        
        image_manager.get_mood_image_path.return_value = "/fake/path/sad.png"
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        window._update_mood_display(
            mood_type=MoodType.SAD,
            confidence=0.75,
            reason="用户情绪低落"
        )
        
        assert "伤心" in window.mood_status.text()
        assert "75%" in window.mood_status.text()
        assert window.mood_reason.text() == "原因: 用户情绪低落"
        
        window.close()
    
    def test_update_mood_display_neutral(self, app, mock_components):
        """测试更新心情显示（中性）"""
        config_manager, mood_manager, image_manager = mock_components
        
        image_manager.get_mood_image_path.return_value = "/fake/path/neutral.png"
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        window._update_mood_display(
            mood_type=MoodType.NEUTRAL,
            confidence=1.0,
            reason="普通对话"
        )
        
        assert "中性" in window.mood_status.text()
        assert "100%" in window.mood_status.text()
        
        window.close()
    
    def test_update_mood_display_no_image(self, app, mock_components):
        """测试无图片时的心情显示"""
        config_manager, mood_manager, image_manager = mock_components
        
        # 模拟图片管理器返回None
        image_manager.get_mood_image_path.return_value = None
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 应该不会崩溃
        window._update_mood_display(
            mood_type=MoodType.HAPPY,
            confidence=0.8,
            reason="测试"
        )
        
        window.close()
    
    def test_add_user_message(self, app, mock_components):
        """测试添加用户消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 添加用户消息
        window._add_user_message("你好，AI宠物！")
        
        # 检查消息是否添加到显示区域
        # 由于QTextBrowser的内部实现，我们检查消息计数
        assert window.message_count > 0
        
        window.close()
    
    def test_add_ai_message(self, app, mock_components):
        """测试添加AI消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 添加AI消息
        window._add_ai_message("你好！我是AI宠物。")
        
        assert window.message_count > 0
        
        window.close()
    
    def test_add_system_message(self, app, mock_components):
        """测试添加系统消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 添加系统消息
        window._add_system_message("系统提示：AI已连接")
        
        assert window.message_count > 0
        
        window.close()
    
    def test_clear_chat_display(self, app, mock_components):
        """测试清空聊天显示"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 先添加一些消息
        window._add_user_message("消息1")
        window._add_ai_message("回复1")
        
        original_count = window.message_count
        
        # 清空显示
        window._clear_chat_display()
        
        # 消息计数应该重置
        assert window.message_count == 0
        
        window.close()
    
    def test_on_send_message(self, app, mock_components):
        """测试发送消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 设置输入文本
        window.chat_input.setText("测试消息")
        
        # 模拟心情分析
        mood_manager.analyze_and_update.return_value = True
        
        # 模拟发送信号
        window.send_message_signal = Mock()
        
        # 调用发送消息
        window._on_send_message()
        
        # 应该发送信号
        window.send_message_signal.emit.assert_called_with("测试消息")
        
        # 输入框应该被清空
        assert window.chat_input.text() == ""
        
        # 应该分析心情
        mood_manager.analyze_and_update.assert_called_with("测试消息")
        
        window.close()
    
    def test_on_send_message_empty(self, app, mock_components):
        """测试发送空消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 设置空文本
        window.chat_input.setText("")
        
        window.send_message_signal = Mock()
        
        # 调用发送消息
        window._on_send_message()
        
        # 不应该发送信号
        window.send_message_signal.emit.assert_not_called()
        
        window.close()
    
    def test_on_send_message_whitespace(self, app, mock_components):
        """测试发送空白消息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 设置空白文本
        window.chat_input.setText("   ")
        
        window.send_message_signal = Mock()
        
        window._on_send_message()
        
        # 不应该发送信号
        window.send_message_signal.emit.assert_not_called()
        
        window.close()
    
    def test_update_ai_response(self, app, mock_components):
        """测试更新AI响应"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 更新AI响应
        window.update_ai_response("这是AI的回复")
        
        # 应该添加了AI消息
        assert window.message_count > 0
        
        window.close()
    
    def test_update_connection_status_connected(self, app, mock_components):
        """测试更新连接状态（已连接）"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 更新为已连接状态
        window.update_connection_status("已连接到AI", True)
        
        # 检查状态标签
        # 注意：实际的颜色设置无法直接测试
        assert window.status_label is not None
        
        window.close()
    
    def test_update_connection_status_disconnected(self, app, mock_components):
        """测试更新连接状态（未连接）"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 更新为未连接状态
        window.update_connection_status("连接失败", False)
        
        assert window.status_label is not None
        
        window.close()
    
    def test_show_error(self, app, mock_components):
        """测试显示错误"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            # 显示错误
            window.show_error("测试错误消息")
            
            # 应该调用了QMessageBox
            mock_critical.assert_called_once()
            
            # 检查参数
            call_args = mock_critical.call_args[0]
            assert call_args[0] == window  # parent
            assert "错误" in call_args[1]  # title
            assert "测试错误消息" in call_args[2]  # message
        
        window.close()
    
    def test_show_info(self, app, mock_components):
        """测试显示信息"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        with patch.object(QMessageBox, 'information') as mock_info:
            # 显示信息
            window.show_info("测试信息", "详细信息")
            
            mock_info.assert_called_once()
            
            call_args = mock_info.call_args[0]
            assert call_args[0] == window
            assert "测试信息" in call_args[1]
            assert "详细信息" in call_args[2]
        
        window.close()
    
    def test_close_event(self, app, mock_components):
        """测试关闭事件"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 模拟关闭信号
        window.close_window_signal = Mock()
        
        # 创建模拟的关闭事件
        mock_event = Mock()
        
        # 触发关闭事件
        window.closeEvent(mock_event)
        
        # 应该发出关闭信号
        window.close_window_signal.emit.assert_called_once()
        
        # 事件应该被接受
        mock_event.accept.assert_called_once()
        
        window.close()
    
    def test_set_chat_manager(self, app, mock_components):
        """测试设置聊天管理器"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 模拟聊天管理器
        chat_manager = Mock()
        
        # 设置聊天管理器
        window.set_chat_manager(chat_manager)
        
        assert window.chat_manager == chat_manager
        
        window.close()
    
    def test_set_ai_manager(self, app, mock_components):
        """测试设置AI管理器"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 模拟AI管理器
        ai_manager = Mock()
        
        # 设置AI管理器
        window.set_ai_manager(ai_manager)
        
        assert window.ai_manager == ai_manager
        
        window.close()
    
    def test_key_press_event_enter(self, app, mock_components):
        """测试按键事件（回车）"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 设置输入文本
        window.chat_input.setText("测试消息")
        
        # 模拟发送消息
        window._on_send_message = Mock()
        
        # 创建模拟的按键事件（回车）
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtCore import QEvent
        
        # 模拟Ctrl+Enter
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.ControlModifier)
        
        # 发送事件到输入框
        QTest.keyPress(window.chat_input, Qt.Key_Return, Qt.ControlModifier)
        
        # 由于事件处理是异步的，我们直接调用处理函数
        window._on_send_message.assert_called_once()
        
        window.close()
    
    def test_load_window_settings(self, app, mock_components):
        """测试加载窗口设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        # 模拟配置
        config_manager.load_config.return_value = {
            "window": {
                "width": 1200,
                "height": 800
            }
        }
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 应该调用了配置管理器
        config_manager.load_config.assert_called_with("settings.json")
        
        window.close()
    
    def test_save_window_settings(self, app, mock_components, temp_dir):
        """测试保存窗口设置"""
        config_manager, mood_manager, image_manager = mock_components
        
        window = MainWindow(config_manager, mood_manager, image_manager)
        
        # 设置窗口大小
        window.resize(1000, 700)
        
        # 模拟保存配置
        config_manager.save_config.return_value = True
        
        # 保存设置
        result = window._save_window_settings()
        
        # 应该调用了配置管理器
        config_manager.save_config.assert_called()
        
        # 检查保存的数据
        call_args = config_manager.save_config.call_args
        config_data = call_args[0][1]  # 第二个参数是数据
        
        assert "window" in config_data
        assert "width" in config_data["window"]
        assert "height" in config_data["window"]
        
        window.close()