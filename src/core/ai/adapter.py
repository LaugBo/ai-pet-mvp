# AI API适配器
# 功能：统一不同AI服务的API接口，提供一致的使用方式
# 修改：简化适配器，专注Ollama连接

from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from .local_network import LocalNetworkConnector

class AIAdapter(ABC):
    """
    AI适配器抽象基类
    定义统一的AI接口
    """
    
    @abstractmethod
    def send_message(self, message: str, **kwargs) -> Optional[str]:
        """发送消息并获取回复"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取AI状态"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查AI是否可用"""
        pass

class OllamaAdapter(AIAdapter):
    """
    Ollama适配器
    专门处理Ollama连接
    """
    
    def __init__(self, ip: str = "localhost", port: int = 11434, model: str = "my-qwen:latest"):
        """
        初始化Ollama适配器
        
        参数:
            ip: 服务器IP地址
            port: 服务器端口
            model: 模型名称
        """
        self.connector = LocalNetworkConnector(
            ip_address=ip,
            port=port,
            ai_type="ollama"
        )
        self.model = model
        self.last_response = None
        
        print(f"Ollama适配器初始化: {ip}:{port}, 模型: {model}")
    
    def send_message(self, message: str, **kwargs) -> Optional[str]:
        """
        发送消息到Ollama
        
        参数:
            message: 消息内容
            **kwargs: 额外参数
            
        返回:
            AI回复内容
        """
        if not self.is_available():
            print("❌ AI不可用，无法发送消息")
            return None
        
        print(f"发送消息到Ollama: {message[:50]}...")
        
        # 准备请求数据
        data = {
            "model": self.model,
            "prompt": message,
            "stream": False
        }
        
        # 添加额外参数
        data.update(kwargs)
        
        # 发送请求
        response = self.connector.send_request("/api/generate", data)
        
        if response:
            # 从Ollama响应中提取回复
            ai_response = response.get("response")
            if ai_response:
                self.last_response = ai_response
                print(f"✅ 收到回复: {ai_response[:50]}...")
                return ai_response
            else:
                print(f"❌ 响应中没有回复内容: {response}")
                return None
        else:
            print("❌ 请求失败，无响应")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取Ollama状态
        
        返回:
            状态信息字典
        """
        info = self.connector.get_ai_info() or {}
        
        status = {
            "type": "ollama",
            "available": self.is_available(),
            "model": self.model,
            "address": self.connector.base_url,
            "last_response_time": self.connector.last_response_time,
            "info": info
        }
        
        return status
    
    def is_available(self) -> bool:
        """
        检查Ollama是否可用
        
        返回:
            是否可用
        """
        return self.connector.test_connection()
    
    def list_models(self) -> list:
        """
        列出Ollama中可用的模型
        
        返回:
            模型列表
        """
        try:
            response = self.connector.session.get(
                f"{self.connector.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [model.get("name") for model in models if model.get("name")]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
        
        return []
    
    def get_model_info(self, model_name: str = None) -> Optional[Dict[str, Any]]:
        """
        获取模型信息
        
        参数:
            model_name: 模型名称，None则使用当前模型
            
        返回:
            模型信息
        """
        model = model_name or self.model
        
        try:
            data = {"name": model}
            response = self.connector.send_request("/api/show", data)
            return response
        except:
            return None

class AIAdapterFactory:
    """
    AI适配器工厂
    根据配置创建合适的适配器
    """
    
    @staticmethod
    def create_adapter(adapter_type: str, **kwargs) -> Optional[AIAdapter]:
        """
        创建适配器
        
        参数:
            adapter_type: 适配器类型，现在只支持 "ollama"
            **kwargs: 适配器参数
            
        返回:
            AI适配器实例
        """
        adapter_type = adapter_type.lower()
        
        if adapter_type == "ollama":
            return OllamaAdapter(**kwargs)
        else:
            print(f"❌ 不支持的适配器类型: {adapter_type}")
            print(f"✅ 当前只支持: ollama")
            return None

# 统一的AI管理器
class AIManager:
    """
    AI管理器
    统一管理AI连接和交互
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化AI管理器
        
        参数:
            config: 配置字典
        """
        self.config = config or {}
        self.adapter = None
        self.message_history = []  # 消息历史
        
        # 从配置创建适配器
        self._init_adapter()
    
    def _init_adapter(self):
        """初始化适配器"""
        # 默认使用ollama适配器
        adapter_type = self.config.get("adapter_type", "ollama")
        
        adapter_config = {
            "ip": self.config.get("ip", "localhost"),
            "port": self.config.get("port", 11434),
            "model": self.config.get("model", "my-qwen:latest")
        }
        
        self.adapter = AIAdapterFactory.create_adapter(adapter_type, **adapter_config)
        
        if self.adapter:
            print(f"✅ AI适配器创建成功: {adapter_type}")
            print(f"   地址: {adapter_config['ip']}:{adapter_config['port']}")
            print(f"   模型: {adapter_config['model']}")
        else:
            print("❌ AI适配器创建失败")
    
    def chat(self, message: str) -> Optional[str]:
        """
        发送聊天消息
        
        参数:
            message: 用户消息
            
        返回:
            AI回复
        """
        if not self.adapter or not self.adapter.is_available():
            print("❌ AI适配器不可用")
            return None
        
        print(f"📤 发送消息: {message}")
        
        # 记录用户消息
        self.message_history.append({
            "role": "user",
            "content": message,
            "timestamp": self._get_timestamp()
        })
        
        # 发送消息
        response = self.adapter.send_message(message)
        
        if response:
            # 记录AI回复
            self.message_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": self._get_timestamp()
            })
            
            print(f"📥 收到回复: {response[:50]}...")
            return response
        else:
            print("❌ 未收到回复")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取AI状态
        
        返回:
            状态信息
        """
        if self.adapter:
            return self.adapter.get_status()
        return {"available": False, "error": "适配器未初始化"}
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_history(self) -> list:
        """
        获取消息历史
        
        返回:
            消息历史列表
        """
        return self.message_history.copy()
    
    def clear_history(self):
        """清空消息历史"""
        self.message_history.clear()
        print("🗑️ 消息历史已清空")

# 使用示例
if __name__ == "__main__":
    print("=" * 50)
    print("AI适配器测试 - Ollama专用")
    print("=" * 50)
    
    # 配置
    config = {
        "adapter_type": "ollama",
        "ip": "localhost",  # 您的AI主机IP
        "port": 11434,
        "model": "my-qwen:latest"
    }
    
    # 创建AI管理器
    ai_manager = AIManager(config)
    
    # 检查状态
    status = ai_manager.get_status()
    print(f"AI状态: {status}")
    
    if status.get("available"):
        # 测试对话
        response = ai_manager.chat("你好，请用中文简单介绍一下自己")
        if response:
            print(f"\nAI回复:\n{response}")
        
        # 查看历史
        print(f"\n消息历史:")
        for msg in ai_manager.get_history():
            print(f"{msg['timestamp']} [{msg['role']}]: {msg['content'][:30]}...")
    else:
        print("❌ AI不可用，请检查连接")