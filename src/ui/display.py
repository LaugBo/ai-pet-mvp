# UI显示组件
# 功能：集成心情系统到UI，显示心情表情和状态

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGroupBox, QTextEdit,
                            QProgressBar, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QPainter, QBrush
import os
from pathlib import Path
from typing import Dict, Any, Optional

class MoodDisplay(QFrame):
    """
    心情显示组件
    显示当前心情状态和表情
    """
    
    # 定义信号
    mood_clicked = pyqtSignal(str)  # 心情被点击
    image_loaded = pyqtSignal(str)  # 图片加载完成
    mood_changed = pyqtSignal(str, str)  # 心情变化 (旧心情, 新心情)
    
    def __init__(self, mood_manager=None, image_manager=None, parent=None):
        """
        初始化心情显示组件
        
        参数:
            mood_manager: 心情管理器实例
            image_manager: 图片管理器实例
            parent: 父组件
        """
        super().__init__(parent)
        
        self.mood_manager = mood_manager
        self.image_manager = image_manager
        self.current_mood = "neutral"
        self.current_confidence = 0.0
        
        # 心情颜色映射
        self.mood_colors = {
            "happy": QColor(255, 215, 0),    # 金色
            "excited": QColor(255, 69, 0),   # 橙色
            "sad": QColor(30, 144, 255),     # 蓝色
            "proud": QColor(50, 205, 50),    # 绿色
            "confused": QColor(147, 112, 219),  # 紫色
            "neutral": QColor(169, 169, 169)  # 灰色
        }
        
        # 心情描述映射
        self.mood_descriptions = {
            "happy": "😊 开心",
            "excited": "🎉 兴奋",
            "sad": "😢 低落",
            "proud": "🏆 自豪",
            "confused": "❓ 困惑",
            "neutral": "😐 中性"
        }
        
        # 当前图片
        self.current_pixmap = None
        self.image_cache = {}
        
        # 动画效果
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_mood)
        self.animation_phase = 0
        self.animation_speed = 50  # 毫秒
        
        # 初始化UI
        self._setup_ui()
        
        # 设置样式
        self._setup_style()
        
        # 启动动画
        self.animation_timer.start(self.animation_speed)
        
        print(f"🎭 心情显示组件初始化完成")
    
    def _setup_ui(self):
        """设置UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # 1. 标题栏
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("AI宠物心情")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        self.title_label.setFont(title_font)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setToolTip("刷新心情")
        self.refresh_btn.clicked.connect(self._refresh_mood)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(title_layout)
        
        # 2. 心情图片显示区域
        self.image_container = QFrame()
        self.image_container.setFixedSize(180, 180)
        self.image_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 3px solid #dee2e6;
                border-radius: 90px;
            }
        """)
        
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # 设置默认图片
        self._set_default_image()
        
        image_layout.addWidget(self.image_label)
        main_layout.addWidget(self.image_container, alignment=Qt.AlignCenter)
        
        # 3. 心情信息区域
        info_group = QGroupBox("心情信息")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        info_layout = QVBoxLayout(info_group)
        
        # 心情名称
        self.mood_name_label = QLabel("心情: 中性")
        mood_name_font = QFont("Microsoft YaHei", 11, QFont.Bold)
        self.mood_name_label.setFont(mood_name_font)
        self.mood_name_label.setStyleSheet("color: #333;")
        
        # 置信度进度条
        confidence_layout = QHBoxLayout()
        confidence_label = QLabel("置信度:")
        confidence_label.setFixedWidth(60)
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setFormat("%p%")
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        confidence_layout.addWidget(confidence_label)
        confidence_layout.addWidget(self.confidence_bar)
        
        # 心情描述
        self.mood_desc_label = QLabel("当前状态正常")
        self.mood_desc_label.setWordWrap(True)
        self.mood_desc_label.setStyleSheet("color: #666; font-style: italic;")
        
        # 添加到布局
        info_layout.addWidget(self.mood_name_label)
        info_layout.addLayout(confidence_layout)
        info_layout.addWidget(self.mood_desc_label)
        
        main_layout.addWidget(info_group)
        
        # 4. 心情历史区域
        history_group = QGroupBox("最近心情")
        history_group.setStyleSheet(info_group.styleSheet())
        
        history_layout = QVBoxLayout(history_group)
        
        self.history_text = QTextEdit()
        self.history_text.setMaximumHeight(100)
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 10pt;
            }
        """)
        self.history_text.setPlaceholderText("心情历史将在这里显示...")
        
        history_layout.addWidget(self.history_text)
        
        main_layout.addWidget(history_group)
        
        # 5. 控制按钮区域
        button_layout = QHBoxLayout()
        
        # 心情详情按钮
        self.details_btn = QPushButton("📊 详情")
        self.details_btn.clicked.connect(self._show_details)
        
        # 测试按钮（开发用）
        self.test_btn = QPushButton("🎭 测试")
        self.test_btn.clicked.connect(self._test_mood_change)
        self.test_btn.setToolTip("测试心情变化")
        
        button_layout.addWidget(self.details_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.test_btn)
        
        main_layout.addLayout(button_layout)
    
    def _setup_style(self):
        """设置组件样式"""
        self.setStyleSheet("""
            MoodDisplay {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
    
    def _set_default_image(self):
        """设置默认图片"""
        default_pixmap = QPixmap(150, 150)
        default_pixmap.fill(QColor(240, 240, 240))
        
        # 绘制默认表情
        painter = QPainter(default_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制笑脸
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(25, 25, 100, 100)
        
        # 绘制眼睛
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(50, 50, 15, 20)
        painter.drawEllipse(85, 50, 15, 20)
        
        # 绘制嘴巴
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(40, 60, 70, 50, 180 * 16, 180 * 16)
        
        painter.end()
        
        self.image_label.setPixmap(default_pixmap)
    
    def load_mood_image(self, mood_name: str) -> bool:
        """
        加载心情图片
        
        参数:
            mood_name: 心情名称
            
        返回:
            是否加载成功
        """
        try:
            if not self.image_manager:
                print("⚠️ 图片管理器未设置")
                return False
            
            # 获取图片路径
            image_path = self.image_manager.get_mood_image(mood_name)
            if not image_path or not os.path.exists(image_path):
                print(f"⚠️ 图片不存在: {mood_name}")
                return False
            
            # 检查缓存
            if image_path in self.image_cache:
                pixmap = self.image_cache[image_path]
            else:
                # 加载图片
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    print(f"❌ 无法加载图片: {image_path}")
                    return False
                
                # 缩放图片
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 缓存图片
                self.image_cache[image_path] = pixmap
            
            # 应用圆角蒙版
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(pixmap))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0, pixmap.width(), pixmap.height(), 75, 75)
            painter.end()
            
            # 设置图片
            self.image_label.setPixmap(rounded)
            self.current_pixmap = rounded
            
            # 发射信号
            self.image_loaded.emit(image_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 加载心情图片失败: {e}")
            return False
    
    def update_mood_display(self, mood_info: Dict[str, Any]):
        """
        更新心情显示
        
        参数:
            mood_info: 心情信息字典
        """
        try:
            old_mood = self.current_mood
            new_mood = mood_info.get("mood", "neutral")
            confidence = mood_info.get("confidence", 0.0)
            
            # 更新当前心情
            self.current_mood = new_mood
            self.current_confidence = confidence
            
            # 更新图片
            image_loaded = self.load_mood_image(new_mood)
            
            if not image_loaded:
                # 使用默认颜色边框
                color = self.mood_colors.get(new_mood, self.mood_colors["neutral"])
                border_color = f"rgb({color.red()}, {color.green()}, {color.blue()})"
                self.image_container.setStyleSheet(f"""
                    QFrame {{
                        background-color: #f8f9fa;
                        border: 3px solid {border_color};
                        border-radius: 90px;
                    }}
                """)
            
            # 更新心情名称
            mood_display = self.mood_descriptions.get(new_mood, f"😐 {new_mood}")
            self.mood_name_label.setText(f"心情: {mood_display}")
            
            # 更新置信度
            confidence_percent = int(confidence * 100)
            self.confidence_bar.setValue(confidence_percent)
            
            # 根据置信度设置进度条颜色
            if confidence_percent >= 80:
                color = "#2ecc71"  # 绿色
            elif confidence_percent >= 60:
                color = "#f39c12"  # 橙色
            elif confidence_percent >= 40:
                color = "#e74c3c"  # 红色
            else:
                color = "#95a5a6"  # 灰色
            
            self.confidence_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #dee2e6;
                    border-radius: 3px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
            
            # 更新描述
            reason = mood_info.get("reason", "当前状态")
            self.mood_desc_label.setText(reason)
            
            # 更新标题颜色
            title_color = self.mood_colors.get(new_mood, self.mood_colors["neutral"])
            title_color_str = f"rgb({title_color.red()}, {title_color.green()}, {title_color.blue()})"
            self.title_label.setStyleSheet(f"color: {title_color_str};")
            
            # 发射心情变化信号
            if old_mood != new_mood:
                self.mood_changed.emit(old_mood, new_mood)
            
            # 添加历史记录
            self._add_to_history(mood_info)
            
            # 触发闪烁动画
            self._trigger_flash_animation()
            
        except Exception as e:
            print(f"❌ 更新心情显示失败: {e}")
    
    def _add_to_history(self, mood_info: Dict[str, Any]):
        """添加到历史记录"""
        try:
            mood_name = mood_info.get("mood", "unknown")
            confidence = mood_info.get("confidence", 0.0)
            reason = mood_info.get("reason", "")
            
            import time
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            confidence_percent = f"{confidence:.0%}"
            
            history_text = f"[{timestamp}] {mood_name}: {reason} ({confidence_percent})\n"
            
            # 添加到历史文本框
            current_text = self.history_text.toPlainText()
            new_text = history_text + current_text
            
            # 限制历史行数
            lines = new_text.split('\n')
            if len(lines) > 20:  # 最多保留20行
                lines = lines[:20]
                new_text = '\n'.join(lines)
            
            self.history_text.setPlainText(new_text)
            
        except Exception as e:
            print(f"❌ 添加历史记录失败: {e}")
    
    def _trigger_flash_animation(self):
        """触发闪烁动画"""
        try:
            # 创建透明度动画
            effect = QGraphicsOpacityEffect(self.image_container)
            self.image_container.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(500)  # 500毫秒
            animation.setStartValue(1.0)
            animation.setKeyValueAt(0.5, 0.3)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.InOutSine)
            
            animation.start()
            
        except Exception as e:
            print(f"❌ 触发动画失败: {e}")
    
    def _animate_mood(self):
        """心情动画效果"""
        try:
            if not self.animation_timer.isActive():
                return
            
            self.animation_phase = (self.animation_phase + 1) % 360
            
            # 呼吸效果
            scale = 1.0 + 0.05 * (1.0 + (self.animation_phase / 180.0))
            
            # 应用缩放变换
            from PyQt5.QtGui import QTransform
            transform = QTransform()
            transform.scale(scale, scale)
            
            # 创建临时pixmap
            if self.current_pixmap and not self.current_pixmap.isNull():
                scaled_pixmap = self.current_pixmap.transformed(
                    transform, Qt.SmoothTransformation
                )
                
                # 保持居中
                x_offset = (scaled_pixmap.width() - 150) // 2
                y_offset = (scaled_pixmap.height() - 150) // 2
                
                cropped = scaled_pixmap.copy(
                    x_offset, y_offset, 150, 150
                )
                
                self.image_label.setPixmap(cropped)
            
        except Exception as e:
            print(f"❌ 动画错误: {e}")
    
    def _refresh_mood(self):
        """刷新心情"""
        try:
            if self.mood_manager:
                current_info = self.mood_manager.get_current_mood_info()
                self.update_mood_display(current_info)
                print("🔄 心情已刷新")
        except Exception as e:
            print(f"❌ 刷新心情失败: {e}")
    
    def _show_details(self):
        """显示心情详情"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            if not self.mood_manager:
                QMessageBox.information(self, "详情", "心情管理器未设置")
                return
            
            # 获取详细信息
            current_info = self.mood_manager.get_current_mood_info()
            history_summary = self.mood_manager.get_mood_history_summary(hours=24)
            recent_moods = self.mood_manager.get_recent_moods(count=5)
            
            # 构建详情文本
            details = f"当前心情详情:\n"
            details += f"  心情: {current_info.get('mood', 'unknown')}\n"
            details += f"  置信度: {current_info.get('confidence', 0):.1%}\n"
            details += f"  持续时间: {current_info.get('duration', 0):.1f}秒\n"
            details += f"  原因: {current_info.get('reason', '')}\n\n"
            
            details += f"24小时统计:\n"
            details += f"  总记录: {history_summary.get('total_records', 0)}次\n"
            details += f"  最常心情: {history_summary.get('most_common_mood', '无')}\n"
            details += f"  平均置信度: {history_summary.get('average_confidence', 0):.1%}\n\n"
            
            details += f"最近心情变化:\n"
            for i, mood in enumerate(recent_moods, 1):
                import datetime
                timestamp = datetime.datetime.fromtimestamp(mood.get('timestamp', 0))
                details += f"  {i}. {mood.get('mood', 'unknown')} ({timestamp:%H:%M})\n"
            
            QMessageBox.information(self, "心情详情", details)
            
        except Exception as e:
            print(f"❌ 显示详情失败: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"获取详情失败: {str(e)}")
    
    def _test_mood_change(self):
        """测试心情变化（开发用）"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            # 测试心情列表
            test_moods = ["happy", "sad", "excited", "proud", "confused"]
            import random
            
            test_mood = random.choice(test_moods)
            test_confidence = random.uniform(0.5, 0.95)
            
            test_info = {
                "mood": test_mood,
                "confidence": test_confidence,
                "reason": f"测试心情变化: {test_mood}"
            }
            
            self.update_mood_display(test_info)
            
            print(f"🎭 测试心情: {test_mood} ({test_confidence:.1%})")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    def set_mood_manager(self, mood_manager):
        """设置心情管理器"""
        self.mood_manager = mood_manager
        
        if mood_manager:
            # 获取当前心情
            current_info = mood_manager.get_current_mood_info()
            self.update_mood_display(current_info)
            
            print("✅ 心情管理器已设置")
    
    def set_image_manager(self, image_manager):
        """设置图片管理器"""
        self.image_manager = image_manager
        print("✅ 图片管理器已设置")
    
    def clear_history(self):
        """清空历史记录"""
        self.history_text.clear()
        print("🗑️ 心情历史已清空")

# 使用示例
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("心情显示组件测试")
    window.setGeometry(100, 100, 400, 600)
    
    # 创建中央组件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 创建心情显示组件
    mood_display = MoodDisplay()
    layout.addWidget(mood_display)
    
    # 测试按钮
    from PyQt5.QtWidgets import QPushButton
    
    def test_happy():
        mood_info = {
            "mood": "happy",
            "confidence": 0.85,
            "reason": "用户说了开心的话"
        }
        mood_display.update_mood_display(mood_info)
    
    def test_sad():
        mood_info = {
            "mood": "sad",
            "confidence": 0.72,
            "reason": "用户表达了难过"
        }
        mood_display.update_mood_display(mood_info)
    
    test_layout = QHBoxLayout()
    
    happy_btn = QPushButton("测试开心")
    happy_btn.clicked.connect(test_happy)
    
    sad_btn = QPushButton("测试低落")
    sad_btn.clicked.connect(test_sad)
    
    test_layout.addWidget(happy_btn)
    test_layout.addWidget(sad_btn)
    
    layout.addLayout(test_layout)
    
    # 显示窗口
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())