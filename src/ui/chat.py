# 聊天管理器
# 功能：管理聊天会话，处理消息发送和接收

import json
import time
from typing import Dict, List, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class ChatWorker(QThread):
    """
    聊天工作线程
    在后台处理AI请求
    """
    
    # 定义信号
    response_received = pyqtSignal(str)  # 收到响应
    error_occurred = pyqtSignal(str)     # 发生错误
    request_complete = pyqtSignal()      # 请求完成
    
    def __init__(self, ai_manager=None):
        """
        初始化聊天工作线程
        
        参数:
            ai_manager: AI管理器实例
        """
        super().__init__()
        self.ai_manager = ai_manager
        self.message = ""
        self.running = False
    
    def set_message(self, message: str):
        """设置要发送的消息"""
        self.message = message
    
    def run(self):
        """线程运行方法"""
        self.running = True
        
        try:
            if not self.ai_manager:
                self.error_occurred.emit("AI管理器未初始化")
                return
            
            # 模拟网络延迟
            time.sleep(0.5)
            
            # 发送消息到AI
            response = self.ai_manager.chat(self.message)
            
            if response:
                self.response_received.emit(response)
            else:
                self.error_occurred.emit("未收到AI回复")
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.request_complete.emit()
            self.running = False
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()

class ChatManager(QObject):
    """
    聊天管理器
    管理聊天会话和消息流
    """
    
    # 定义信号
    message_sent = pyqtSignal(str)           # 消息已发送
    response_received = pyqtSignal(str)      # 收到响应
    error_occurred = pyqtSignal(str)         # 发生错误
    status_changed = pyqtSignal(str, bool)   # 状态变化
    
    def __init__(self, config_manager=None, ai_manager=None):
        """
        初始化聊天管理器
        
        参数:
            config_manager: 配置管理器实例
            ai_manager: AI管理器实例
        """
        super().__init__()
        
        self.config_manager = config_manager
        self.ai_manager = ai_manager
        
        # 聊天状态
        self.is_connected = False
        self.is_processing = False
        self.conversation_history = []
        self.max_history = 50
        
        # 工作线程
        self.worker = None
        
        # 从配置加载设置
        self._load_config()
        
        print("聊天管理器初始化完成")
    
    def _load_config(self):
        """加载配置"""
        if self.config_manager:
            self.max_history = self.config_manager.get_config_value(
                "settings.json", "memory.max_conversation_history", 50
            )
    
    def connect_ai(self) -> bool:
        """
        连接AI服务器
        
        返回:
            是否连接成功
        """
        try:
            if not self.ai_manager:
                self.status_changed.emit("AI管理器未初始化", False)
                return False
            
            # 获取AI状态
            status = self.ai_manager.get_status()
            
            if status.get("available", False):
                self.is_connected = True
                self.status_changed.emit("已连接到AI", True)
                return True
            else:
                self.status_changed.emit("AI不可用", False)
                return False
                
        except Exception as e:
            self.status_changed.emit(f"连接失败: {str(e)}", False)
            return False
    
    def send_message(self, message: str) -> bool:
        """
        发送消息
        
        参数:
            message: 消息内容
            
        返回:
            是否发送成功
        """
        if not message or not message.strip():
            self.error_occurred.emit("消息不能为空")
            return False
        
        if not self.is_connected:
            self.error_occurred.emit("未连接到AI")
            return False
        
        if self.is_processing:
            self.error_occurred.emit("正在处理上一个请求")
            return False
        
        # 设置处理状态
        self.is_processing = True
        
        # 保存到历史
        self._add_to_history("user", message)
        
        # 发送消息信号
        self.message_sent.emit(message)
        
        # 在工作线程中处理AI请求
        self._start_worker(message)
        
        return True
    
    def _start_worker(self, message: str):
        """启动工作线程处理AI请求"""
        # 停止之前的线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        
        # 创建新线程
        self.worker = ChatWorker(self.ai_manager)
        self.worker.set_message(message)
        
        # 连接信号
        self.worker.response_received.connect(self._handle_response)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.request_complete.connect(self._handle_request_complete)
        
        # 启动线程
        self.worker.start()
    
    @pyqtSlot(str)
    def _handle_response(self, response: str):
        """处理AI响应"""
        # 保存到历史
        self._add_to_history("assistant", response)
        
        # 发射信号
        self.response_received.emit(response)
    
    @pyqtSlot(str)
    def _handle_error(self, error: str):
        """处理错误"""
        self.error_occurred.emit(error)
    
    @pyqtSlot()
    def _handle_request_complete(self):
        """处理请求完成"""
        self.is_processing = False
    
    def _add_to_history(self, role: str, content: str):
        """
        添加到历史记录
        
        参数:
            role: 角色 (user/assistant)
            content: 内容
        """
        timestamp = time.time()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        self.conversation_history.append(message)
        
        # 限制历史记录长度
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        参数:
            limit: 限制条数，None表示全部
            
        返回:
            对话历史列表
        """
        if limit and limit > 0:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def get_formatted_history(self) -> str:
        """获取格式化的对话历史"""
        formatted = []
        for msg in self.conversation_history:
            role = "👤 你" if msg["role"] == "user" else "🤖 AI"
            time_str = time.strftime("%H:%M:%S", time.localtime(msg["timestamp"]))
            formatted.append(f"[{time_str}] {role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def save_conversation(self, filename: str = None) -> bool:
        """
        保存对话历史到文件
        
        参数:
            filename: 文件名，None则自动生成
            
        返回:
            是否保存成功
        """
        try:
            if not filename:
                # 自动生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"conversation_{timestamp}.json"
            
            data = {
                "version": "1.0",
                "timestamp": time.time(),
                "message_count": len(self.conversation_history),
                "messages": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存对话失败: {e}")
            return False
    
    def load_conversation(self, filename: str) -> bool:
        """
        从文件加载对话历史
        
        参数:
            filename: 文件名
            
        返回:
            是否加载成功
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "messages" in data:
                self.conversation_history = data["messages"]
                return True
            else:
                return False
                
        except Exception as e:
            print(f"加载对话失败: {e}")
            return False
    
    def clear_conversation(self):
        """清空对话历史"""
        self.conversation_history.clear()
    
    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        
        # 停止工作线程
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        
        self.status_changed.emit("已断开连接", False)
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取状态信息
        
        返回:
            状态字典
        """
        return {
            "connected": self.is_connected,
            "processing": self.is_processing,
            "message_count": len(self.conversation_history),
            "ai_available": self.ai_manager is not None
        }