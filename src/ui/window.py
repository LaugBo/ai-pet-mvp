# 主窗口 - 程序主界面
# 功能：创建和管理主窗口，包含所有UI组件
# 更新：集成心情显示组件

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QLineEdit,
                            QSplitter, QStatusBar, QMessageBox,
                            QTabWidget, QDockWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
import os

# 导入新增的UI组件
from .display import MoodDisplay

class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 定义信号
    send_message_signal = pyqtSignal(str)  # 发送消息信号
    close_window_signal = pyqtSignal()     # 关闭窗口信号
    
    def __init__(self, config_manager=None, mood_manager=None, image_manager=None):
        """
        初始化主窗口
        
        参数:
            config_manager: 配置管理器实例
            mood_manager: 心情管理器实例
            image_manager: 图片管理器实例
        """
        super().__init__()
        
        self.config_manager = config_manager
        self.mood_manager = mood_manager
        self.image_manager = image_manager
        self.message_history = []  # 消息历史
        
        # 加载配置
        self._load_config()
        
        # 初始化UI
        self._setup_ui()
        
        # 设置窗口属性
        self._setup_window()
        
        # 设置心情管理器
        if self.mood_manager:
            self._setup_mood_system()
        
        print("主窗口初始化完成")
    
    def _load_config(self):
        """加载UI配置"""
        if self.config_manager:
            # 从配置获取设置
            self.window_width = self.config_manager.get_config_value(
                "settings.json", "ui.window_width", 1000
            )
            self.window_height = self.config_manager.get_config_value(
                "settings.json", "ui.window_height", 700
            )
            self.app_name = self.config_manager.get_config_value(
                "settings.json", "app.name", "AI宠物MVP"
            )
            self.font_family = self.config_manager.get_config_value(
                "settings.json", "ui.font_family", "Microsoft YaHei"
            )
            self.font_size = self.config_manager.get_config_value(
                "settings.json", "ui.font_size", 11
            )
        else:
            # 默认配置
            self.window_width = 1000
            self.window_height = 700
            self.app_name = "AI宠物MVP"
            self.font_family = "Microsoft YaHei"
            self.font_size = 11
    
    def _setup_window(self):
        """设置窗口属性"""
        # 设置窗口标题
        self.setWindowTitle(self.app_name)
        
        # 设置窗口大小
        self.resize(self.window_width, self.window_height)
        
        # 设置最小大小
        self.setMinimumSize(800, 500)
        
        # 设置字体
        font = QFont(self.font_family, self.font_size)
        self.setFont(font)
        
        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _setup_ui(self):
        """设置UI布局和组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 左侧区域：聊天界面
        self.chat_area = self._create_chat_area()
        main_layout.addWidget(self.chat_area, stretch=3)
        
        # 右侧区域：心情显示
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar, stretch=1)
    
    def _create_chat_area(self):
        """创建聊天区域"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(5, 5, 5, 5)
        chat_layout.setSpacing(5)
        
        # 1. 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel("💬 对话")
        title_font = QFont(self.font_family, 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # AI状态指示器
        self.ai_status_label = QLabel("● 离线")
        self.ai_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.ai_status_label)
        
        chat_layout.addLayout(title_layout)
        
        # 2. 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 12pt;
                min-height: 300px;
            }
        """)
        self.chat_display.setPlaceholderText("消息将在这里显示...\n与AI宠物开始对话吧！")
        
        chat_layout.addWidget(self.chat_display, stretch=3)
        
        # 3. 输入区域
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(0, 5, 0, 0)
        
        # 输入框
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("输入消息... (Ctrl+Enter发送)")
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                font-size: 12pt;
            }
            QTextEdit:focus {
                border: 2px solid #2980b9;
            }
        """)
        
        # 设置Ctrl+Enter发送
        self.message_input.keyPressEvent = self._handle_key_press
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setFixedHeight(35)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self._clear_chat)
        
        # 发送按钮
        self.send_button = QPushButton("📤 发送 (Ctrl+Enter)")
        self.send_button.setFixedHeight(35)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        
        # 添加到布局
        input_layout.addWidget(self.message_input)
        input_layout.addLayout(button_layout)
        
        chat_layout.addWidget(input_group, stretch=1)
        
        return chat_widget
    
    def _create_sidebar(self):
        """创建侧边栏（心情显示）"""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(5)
        
        # 侧边栏标题
        sidebar_title = QLabel("🎭 AI宠物")
        sidebar_title_font = QFont(self.font_family, 14, QFont.Bold)
        sidebar_title.setFont(sidebar_title_font)
        sidebar_title.setStyleSheet("color: #2c3e50;")
        sidebar_title.setAlignment(Qt.AlignCenter)
        
        sidebar_layout.addWidget(sidebar_title)
        
        # 创建心情显示组件
        self.mood_display = MoodDisplay(self.mood_manager, self.image_manager)
        
        # 连接心情变化信号
        self.mood_display.mood_changed.connect(self._on_mood_changed)
        
        sidebar_layout.addWidget(self.mood_display)
        
        # 添加一些信息面板
        info_group = self._create_info_panel()
        sidebar_layout.addWidget(info_group)
        
        return sidebar_widget
    
    def _create_info_panel(self):
        """创建信息面板"""
        info_group = QWidget()
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(5)
        
        # 连接状态
        conn_group = QWidget()
        conn_layout = QHBoxLayout(conn_group)
        conn_layout.setContentsMargins(0, 0, 0, 0)
        
        conn_label = QLabel("连接状态:")
        self.connection_status_label = QLabel("未连接")
        self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        conn_layout.addWidget(conn_label)
        conn_layout.addStretch()
        conn_layout.addWidget(self.connection_status_label)
        
        info_layout.addWidget(conn_group)
        
        # 消息统计
        stats_group = QWidget()
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_label = QLabel("消息统计:")
        self.message_count_label = QLabel("0 条")
        
        stats_layout.addWidget(stats_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.message_count_label)
        
        info_layout.addWidget(stats_group)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        info_layout.addWidget(separator)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setFixedHeight(30)
        settings_btn.clicked.connect(self._show_settings)
        
        # 关于按钮
        about_btn = QPushButton("ℹ️ 关于")
        about_btn.setFixedHeight(30)
        about_btn.clicked.connect(self._show_about)
        
        control_layout.addWidget(settings_btn)
        control_layout.addStretch()
        control_layout.addWidget(about_btn)
        
        info_layout.addLayout(control_layout)
        
        return info_group
    
    def _setup_mood_system(self):
        """设置心情系统"""
        if self.mood_manager and hasattr(self, 'mood_display'):
            # 设置心情管理器
            self.mood_display.set_mood_manager(self.mood_manager)
            
            # 如果有图片管理器，也设置
            if self.image_manager and hasattr(self.mood_display, 'set_image_manager'):
                self.mood_display.set_image_manager(self.image_manager)
            
            print("✅ 心情系统设置完成")
    
    def _on_mood_changed(self, old_mood: str, new_mood: str):
        """处理心情变化"""
        # 在状态栏显示心情变化
        mood_names = {
            "happy": "开心",
            "excited": "兴奋",
            "sad": "低落",
            "proud": "自豪",
            "confused": "困惑",
            "neutral": "中性"
        }
        
        old_name = mood_names.get(old_mood, old_mood)
        new_name = mood_names.get(new_mood, new_mood)
        
        self.status_bar.showMessage(f"心情变化: {old_name} → {new_name}", 3000)
        
        # 在聊天区域添加系统消息
        self._add_system_message(f"AI宠物心情变化: {old_name} → {new_name}")
    
    def _add_system_message(self, message: str):
        """添加系统消息到聊天"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_html = f"""
        <div style="margin: 5px 0; text-align: center;">
            <div style="
                display: inline-block;
                background-color: #f1f8ff;
                border: 1px solid #c8e1ff;
                border-radius: 5px;
                padding: 5px 10px;
                color: #0366d6;
                font-size: 10pt;
                font-style: italic;
            ">
                {message} <span style="color: #888; font-size: 9pt;">{timestamp}</span>
            </div>
        </div>
        """
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(message_html)
        cursor.insertText("\n")
        
        # 自动滚动到底部
        self._scroll_to_bottom()
    
    def _handle_key_press(self, event):
        """处理键盘事件"""
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtCore import QCoreApplication
        
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
           (event.modifiers() & Qt.ControlModifier):
            self._send_message()
        else:
            from PyQt5.QtWidgets import QTextEdit
            QTextEdit.keyPressEvent(self.message_input, event)
    
    def _send_message(self):
        """发送消息"""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "提示", "消息不能为空！")
            return
        
        # 显示用户消息
        self._add_message_to_display("👤 你", message, is_user=True)
        
        # 清空输入框
        self.message_input.clear()
        
        # 添加思考中消息
        self._add_message_to_display("🤔 AI宠物", "正在思考...", is_user=False)
        
        # 发送信号
        self.send_message_signal.emit(message)
        
        # 更新消息计数
        self._update_message_count()
        
        # 分析心情
        if self.mood_manager:
            self._analyze_message_mood(message)
    
    def _analyze_message_mood(self, message: str):
        """分析消息心情"""
        try:
            from src.core.mood.analyzer import MoodAnalyzer
            
            # 创建分析器
            analyzer = MoodAnalyzer()
            result = analyzer.analyze_text(message)
            
            # 如果有心情管理器，更新心情
            if self.mood_manager and result.confidence > 0.3:
                from src.core.mood.manager import MoodResult
                
                # 转换结果格式
                mood_result = MoodResult(
                    mood_type=result.mood_type,
                    confidence=result.confidence,
                    triggers=result.triggers,
                    reason=result.reason
                )
                
                # 更新心情
                self.mood_manager._update_mood(mood_result)
                
                # 更新显示
                if hasattr(self, 'mood_display'):
                    current_info = self.mood_manager.get_current_mood_info()
                    self.mood_display.update_mood_display(current_info)
        
        except Exception as e:
            print(f"❌ 分析消息心情失败: {e}")
    
    def _add_message_to_display(self, sender: str, message: str, is_user: bool = True):
        """添加消息到显示区域"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_user:
            bg_color = "#e3f2fd"
            align = "right"
            sender_color = "#1976d2"
        else:
            bg_color = "#f5f5f5"
            align = "left"
            sender_color = "#d32f2f"
        
        message_html = f"""
        <div style="margin: 10px 0; text-align: {align};">
            <div style="
                display: inline-block;
                max-width: 80%;
                background-color: {bg_color};
                border-radius: 10px;
                padding: 10px 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <div style="
                    color: {sender_color};
                    font-weight: bold;
                    font-size: 11pt;
                    margin-bottom: 5px;
                ">
                    {sender} <span style="color: #888; font-size: 9pt;">{timestamp}</span>
                </div>
                <div style="
                    color: #333;
                    font-size: 12pt;
                    line-height: 1.4;
                ">
                    {message.replace('\n', '<br>')}
                </div>
            </div>
        </div>
        """
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(message_html)
        cursor.insertText("\n\n")
        
        # 保存到历史
        self.message_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "is_user": is_user
        })
    
    def _update_message_count(self):
        """更新消息计数"""
        count = len([m for m in self.message_history if m["is_user"]])
        self.message_count_label.setText(f"{count} 条")
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _clear_chat(self):
        """清空聊天"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有聊天记录吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.message_history.clear()
            self._update_message_count()
            self.status_bar.showMessage("聊天记录已清空", 3000)
    
    def _show_settings(self):
        """显示设置对话框"""
        settings_text = "AI宠物MVP 设置\n\n"
        settings_text += f"版本: 1.0.0\n"
        settings_text += f"窗口大小: {self.width()}x{self.height()}\n"
        settings_text += f"字体: {self.font_family} {self.font_size}pt\n\n"
        
        if self.mood_manager:
            current_mood = self.mood_manager.get_current_mood_info()
            settings_text += f"当前心情: {current_mood.get('mood', '未知')}\n"
        
        QMessageBox.information(self, "设置", settings_text)
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = "AI宠物MVP\n\n"
        about_text += "一个带有心情系统的AI对话伴侣\n\n"
        about_text += "功能特性:\n"
        about_text += "• 智能AI对话\n"
        about_text += "• 动态心情系统\n"
        about_text += "• 记忆存储功能\n"
        about_text += "• 漂亮的用户界面\n\n"
        about_text += "基于 PyQt5 和 Ollama 构建"
        
        QMessageBox.about(self, "关于", about_text)
    
    def update_ai_response(self, response: str):
        """更新AI回复"""
        # 移除"正在思考..."消息
        self._remove_last_message()
        
        # 添加AI回复
        self._add_message_to_display("🤖 AI宠物", response, is_user=False)
        
        # 更新AI状态
        self.ai_status_label.setText("● 在线")
        self.ai_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        # 更新连接状态
        self.connection_status_label.setText("已连接")
        self.connection_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        # 分析AI回复的心情
        if self.mood_manager:
            self._analyze_message_mood(response)
        
        # 自动滚动
        self._scroll_to_bottom()
        
        # 更新状态栏
        self.status_bar.showMessage("收到AI回复", 3000)
    
    def _remove_last_message(self):
        """移除最后一条消息"""
        # 获取当前文本
        current_text = self.chat_display.toHtml()
        
        # 查找最后一个消息块
        messages = current_text.split("</div>\n\n")
        if len(messages) > 1:
            new_text = "</div>\n\n".join(messages[:-1])
            self.chat_display.setHtml(new_text)
        
        # 从历史中移除
        if self.message_history and not self.message_history[-1]["is_user"]:
            self.message_history.pop()
    
    def show_error(self, error_message: str):
        """显示错误信息"""
        # 移除"正在思考..."消息
        self._remove_last_message()
        
        # 显示错误消息
        self._add_message_to_display("❌ 系统", f"错误: {error_message}", is_user=False)
        
        # 更新状态
        self.ai_status_label.setText("● 错误")
        self.ai_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.connection_status_label.setText("连接失败")
        self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        # 更新状态栏
        self.status_bar.showMessage(f"错误: {error_message}", 5000)
    
    def update_connection_status(self, status: str, is_connected: bool = False):
        """更新连接状态"""
        self.connection_status_label.setText(f"{status}")
        if is_connected:
            self.connection_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, "退出", "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发送关闭信号
            self.close_window_signal.emit()
            event.accept()
        else:
            event.ignore()

# 使用示例
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())# 主窗口 - 程序主界面
# 功能：创建和管理主窗口，包含所有UI组件
# 更新：集成心情显示组件

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QLineEdit,
                            QSplitter, QStatusBar, QMessageBox,
                            QTabWidget, QDockWidget, QFrame)  # 添加 QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
import os

# 导入新增的UI组件
from .display import MoodDisplay

class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 定义信号
    send_message_signal = pyqtSignal(str)  # 发送消息信号
    close_window_signal = pyqtSignal()     # 关闭窗口信号
    
    def __init__(self, config_manager=None, mood_manager=None, image_manager=None):
        """
        初始化主窗口
        
        参数:
            config_manager: 配置管理器实例
            mood_manager: 心情管理器实例
            image_manager: 图片管理器实例
        """
        super().__init__()
        
        self.config_manager = config_manager
        self.mood_manager = mood_manager
        self.image_manager = image_manager
        self.message_history = []  # 消息历史
        
        # 加载配置
        self._load_config()
        
        # 初始化UI
        self._setup_ui()
        
        # 设置窗口属性
        self._setup_window()
        
        # 设置心情管理器
        if self.mood_manager:
            self._setup_mood_system()
        
        print("主窗口初始化完成")
    
    def _load_config(self):
        """加载UI配置"""
        if self.config_manager:
            # 从配置获取设置
            self.window_width = self.config_manager.get_config_value(
                "settings.json", "ui.window_width", 1000
            )
            self.window_height = self.config_manager.get_config_value(
                "settings.json", "ui.window_height", 700
            )
            self.app_name = self.config_manager.get_config_value(
                "settings.json", "app.name", "AI宠物MVP"
            )
            self.font_family = self.config_manager.get_config_value(
                "settings.json", "ui.font_family", "Microsoft YaHei"
            )
            self.font_size = self.config_manager.get_config_value(
                "settings.json", "ui.font_size", 11
            )
        else:
            # 默认配置
            self.window_width = 1000
            self.window_height = 700
            self.app_name = "AI宠物MVP"
            self.font_family = "Microsoft YaHei"
            self.font_size = 11
    
    def _setup_window(self):
        """设置窗口属性"""
        # 设置窗口标题
        self.setWindowTitle(self.app_name)
        
        # 设置窗口大小
        self.resize(self.window_width, self.window_height)
        
        # 设置最小大小
        self.setMinimumSize(800, 500)
        
        # 设置字体
        font = QFont(self.font_family, self.font_size)
        self.setFont(font)
        
        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _setup_ui(self):
        """设置UI布局和组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 左侧区域：聊天界面
        self.chat_area = self._create_chat_area()
        main_layout.addWidget(self.chat_area, stretch=3)
        
        # 右侧区域：心情显示
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar, stretch=1)
    
    def _create_chat_area(self):
        """创建聊天区域"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(5, 5, 5, 5)
        chat_layout.setSpacing(5)
        
        # 1. 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel("💬 对话")
        title_font = QFont(self.font_family, 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # AI状态指示器
        self.ai_status_label = QLabel("● 离线")
        self.ai_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.ai_status_label)
        
        chat_layout.addLayout(title_layout)
        
        # 2. 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 12pt;
                min-height: 300px;
            }
        """)
        self.chat_display.setPlaceholderText("消息将在这里显示...\n与AI宠物开始对话吧！")
        
        chat_layout.addWidget(self.chat_display, stretch=3)
        
        # 3. 输入区域
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(0, 5, 0, 0)
        
        # 输入框
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("输入消息... (Ctrl+Enter发送)")
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                font-size: 12pt;
            }
            QTextEdit:focus {
                border: 2px solid #2980b9;
            }
        """)
        
        # 设置Ctrl+Enter发送
        self.message_input.keyPressEvent = self._handle_key_press
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setFixedHeight(35)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self._clear_chat)
        
        # 发送按钮
        self.send_button = QPushButton("📤 发送 (Ctrl+Enter)")
        self.send_button.setFixedHeight(35)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        
        # 添加到布局
        input_layout.addWidget(self.message_input)
        input_layout.addLayout(button_layout)
        
        chat_layout.addWidget(input_group, stretch=1)
        
        return chat_widget
    
    def _create_sidebar(self):
        """创建侧边栏（心情显示）"""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(5)
        
        # 侧边栏标题
        sidebar_title = QLabel("🎭 AI宠物")
        sidebar_title_font = QFont(self.font_family, 14, QFont.Bold)
        sidebar_title.setFont(sidebar_title_font)
        sidebar_title.setStyleSheet("color: #2c3e50;")
        sidebar_title.setAlignment(Qt.AlignCenter)
        
        sidebar_layout.addWidget(sidebar_title)
        
        # 创建心情显示组件
        self.mood_display = MoodDisplay(self.mood_manager, self.image_manager)
        
        # 连接心情变化信号
        self.mood_display.mood_changed.connect(self._on_mood_changed)
        
        sidebar_layout.addWidget(self.mood_display)
        
        # 添加一些信息面板
        info_group = self._create_info_panel()
        sidebar_layout.addWidget(info_group)
        
        return sidebar_widget
    
    def _create_info_panel(self):
        """创建信息面板"""
        info_group = QWidget()
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(5)
        
        # 连接状态
        conn_group = QWidget()
        conn_layout = QHBoxLayout(conn_group)
        conn_layout.setContentsMargins(0, 0, 0, 0)
        
        conn_label = QLabel("连接状态:")
        self.connection_status_label = QLabel("未连接")
        self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        conn_layout.addWidget(conn_label)
        conn_layout.addStretch()
        conn_layout.addWidget(self.connection_status_label)
        
        info_layout.addWidget(conn_group)
        
        # 消息统计
        stats_group = QWidget()
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_label = QLabel("消息统计:")
        self.message_count_label = QLabel("0 条")
        
        stats_layout.addWidget(stats_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.message_count_label)
        
        info_layout.addWidget(stats_group)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        info_layout.addWidget(separator)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setFixedHeight(30)
        settings_btn.clicked.connect(self._show_settings)
        
        # 关于按钮
        about_btn = QPushButton("ℹ️ 关于")
        about_btn.setFixedHeight(30)
        about_btn.clicked.connect(self._show_about)
        
        control_layout.addWidget(settings_btn)
        control_layout.addStretch()
        control_layout.addWidget(about_btn)
        
        info_layout.addLayout(control_layout)
        
        return info_group
    
    def _setup_mood_system(self):
        """设置心情系统"""
        if self.mood_manager and hasattr(self, 'mood_display'):
            # 设置心情管理器
            self.mood_display.set_mood_manager(self.mood_manager)
            
            # 如果有图片管理器，也设置
            if self.image_manager and hasattr(self.mood_display, 'set_image_manager'):
                self.mood_display.set_image_manager(self.image_manager)
            
            print("✅ 心情系统设置完成")
    
    def _on_mood_changed(self, old_mood: str, new_mood: str):
        """处理心情变化"""
        # 在状态栏显示心情变化
        mood_names = {
            "happy": "开心",
            "excited": "兴奋",
            "sad": "低落",
            "proud": "自豪",
            "confused": "困惑",
            "neutral": "中性"
        }
        
        old_name = mood_names.get(old_mood, old_mood)
        new_name = mood_names.get(new_mood, new_mood)
        
        self.status_bar.showMessage(f"心情变化: {old_name} → {new_name}", 3000)
        
        # 在聊天区域添加系统消息
        self._add_system_message(f"AI宠物心情变化: {old_name} → {new_name}")
    
    def _add_system_message(self, message: str):
        """添加系统消息到聊天"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_html = f"""
        <div style="margin: 5px 0; text-align: center;">
            <div style="
                display: inline-block;
                background-color: #f1f8ff;
                border: 1px solid #c8e1ff;
                border-radius: 5px;
                padding: 5px 10px;
                color: #0366d6;
                font-size: 10pt;
                font-style: italic;
            ">
                {message} <span style="color: #888; font-size: 9pt;">{timestamp}</span>
            </div>
        </div>
        """
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(message_html)
        cursor.insertText("\n")
        
        # 自动滚动到底部
        self._scroll_to_bottom()
    
    def _handle_key_press(self, event):
        """处理键盘事件"""
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtCore import QCoreApplication
        
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
           (event.modifiers() & Qt.ControlModifier):
            self._send_message()
        else:
            from PyQt5.QtWidgets import QTextEdit
            QTextEdit.keyPressEvent(self.message_input, event)
    
    def _send_message(self):
        """发送消息"""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "提示", "消息不能为空！")
            return
        
        # 显示用户消息
        self._add_message_to_display("👤 你", message, is_user=True)
        
        # 清空输入框
        self.message_input.clear()
        
        # 添加思考中消息
        self._add_message_to_display("🤔 AI宠物", "正在思考...", is_user=False)
        
        # 发送信号
        self.send_message_signal.emit(message)
        
        # 更新消息计数
        self._update_message_count()
        
        # 分析心情
        if self.mood_manager:
            self._analyze_message_mood(message)
    
    def _analyze_message_mood(self, message: str):
        """分析消息心情"""
        try:
            from src.core.mood.analyzer import MoodAnalyzer
            
            # 创建分析器
            analyzer = MoodAnalyzer()
            result = analyzer.analyze_text(message)
            
            # 如果有心情管理器，更新心情
            if self.mood_manager and result.confidence > 0.3:
                from src.core.mood.manager import MoodResult
                
                # 转换结果格式
                mood_result = MoodResult(
                    mood_type=result.mood_type,
                    confidence=result.confidence,
                    triggers=result.triggers,
                    reason=result.reason
                )
                
                # 更新心情
                self.mood_manager._update_mood(mood_result)
                
                # 更新显示
                if hasattr(self, 'mood_display'):
                    current_info = self.mood_manager.get_current_mood_info()
                    self.mood_display.update_mood_display(current_info)
        
        except Exception as e:
            print(f"❌ 分析消息心情失败: {e}")
    
    def _add_message_to_display(self, sender: str, message: str, is_user: bool = True):
        """添加消息到显示区域"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_user:
            bg_color = "#e3f2fd"
            align = "right"
            sender_color = "#1976d2"
        else:
            bg_color = "#f5f5f5"
            align = "left"
            sender_color = "#d32f2f"
        
        message_html = f"""
        <div style="margin: 10px 0; text-align: {align};">
            <div style="
                display: inline-block;
                max-width: 80%;
                background-color: {bg_color};
                border-radius: 10px;
                padding: 10px 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <div style="
                    color: {sender_color};
                    font-weight: bold;
                    font-size: 11pt;
                    margin-bottom: 5px;
                ">
                    {sender} <span style="color: #888; font-size: 9pt;">{timestamp}</span>
                </div>
                <div style="
                    color: #333;
                    font-size: 12pt;
                    line-height: 1.4;
                ">
                    {message.replace('\n', '<br>')}
                </div>
            </div>
        </div>
        """
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertHtml(message_html)
        cursor.insertText("\n\n")
        
        # 保存到历史
        self.message_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "is_user": is_user
        })
    
    def _update_message_count(self):
        """更新消息计数"""
        count = len([m for m in self.message_history if m["is_user"]])
        self.message_count_label.setText(f"{count} 条")
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _clear_chat(self):
        """清空聊天"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有聊天记录吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.message_history.clear()
            self._update_message_count()
            self.status_bar.showMessage("聊天记录已清空", 3000)
    
    def _show_settings(self):
        """显示设置对话框"""
        settings_text = "AI宠物MVP 设置\n\n"
        settings_text += f"版本: 1.0.0\n"
        settings_text += f"窗口大小: {self.width()}x{self.height()}\n"
        settings_text += f"字体: {self.font_family} {self.font_size}pt\n\n"
        
        if self.mood_manager:
            current_mood = self.mood_manager.get_current_mood_info()
            settings_text += f"当前心情: {current_mood.get('mood', '未知')}\n"
        
        QMessageBox.information(self, "设置", settings_text)
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = "AI宠物MVP\n\n"
        about_text += "一个带有心情系统的AI对话伴侣\n\n"
        about_text += "功能特性:\n"
        about_text += "• 智能AI对话\n"
        about_text += "• 动态心情系统\n"
        about_text += "• 记忆存储功能\n"
        about_text += "• 漂亮的用户界面\n\n"
        about_text += "基于 PyQt5 和 Ollama 构建"
        
        QMessageBox.about(self, "关于", about_text)
    
    def update_ai_response(self, response: str):
        """更新AI回复"""
        # 移除"正在思考..."消息
        self._remove_last_message()
        
        # 添加AI回复
        self._add_message_to_display("🤖 AI宠物", response, is_user=False)
        
        # 更新AI状态
        self.ai_status_label.setText("● 在线")
        self.ai_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        # 更新连接状态
        self.connection_status_label.setText("已连接")
        self.connection_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        # 分析AI回复的心情
        if self.mood_manager:
            self._analyze_message_mood(response)
        
        # 自动滚动
        self._scroll_to_bottom()
        
        # 更新状态栏
        self.status_bar.showMessage("收到AI回复", 3000)
    
    def _remove_last_message(self):
        """移除最后一条消息"""
        # 获取当前文本
        current_text = self.chat_display.toHtml()
        
        # 查找最后一个消息块
        messages = current_text.split("</div>\n\n")
        if len(messages) > 1:
            new_text = "</div>\n\n".join(messages[:-1])
            self.chat_display.setHtml(new_text)
        
        # 从历史中移除
        if self.message_history and not self.message_history[-1]["is_user"]:
            self.message_history.pop()
    
    def show_error(self, error_message: str):
        """显示错误信息"""
        # 移除"正在思考..."消息
        self._remove_last_message()
        
        # 显示错误消息
        self._add_message_to_display("❌ 系统", f"错误: {error_message}", is_user=False)
        
        # 更新状态
        self.ai_status_label.setText("● 错误")
        self.ai_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.connection_status_label.setText("连接失败")
        self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        # 更新状态栏
        self.status_bar.showMessage(f"错误: {error_message}", 5000)
    
    def update_connection_status(self, status: str, is_connected: bool = False):
        """更新连接状态"""
        self.connection_status_label.setText(f"{status}")
        if is_connected:
            self.connection_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.connection_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, "退出", "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发送关闭信号
            self.close_window_signal.emit()
            event.accept()
        else:
            event.ignore()

# 使用示例
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())