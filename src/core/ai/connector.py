#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI连接器 - 核心连接功能
功能：负责与AI服务器通信，发送请求和接收响应
包含：AIConnector 和 OllamaConnector
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class AIConnector:
    """
    AI连接器类
    负责与AI服务器建立连接和通信
    """
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        """
        初始化AI连接器
        
        参数:
            base_url: AI服务器基础地址
            timeout: 请求超时时间（秒）
        """
        # 设置默认值为Ollama地址
        self.base_url = base_url or ""
        self.timeout = timeout
        self.session = requests.Session()  # 创建会话，提高连接效率
        self.last_response_time = None  # 记录上次响应时间
        
        # 设置请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        print(f"🔌 AI连接器初始化完成")
        print(f"  服务器地址: {self.base_url}")
        print(f"  超时时间: {self.timeout}秒")
    
    def test_connection(self) -> bool:
        """
        测试与AI服务器的连接
        
        返回:
            bool: 连接是否成功
        """
        print(f"🔍 测试连接到: {self.base_url}")
        
        try:
            # Ollama的健康检查端点
            response = self.session.get(
                f"{self.base_url}/",
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ 连接测试成功!")
                return True
            else:
                print(f"❌ 连接失败，状态码: {response.status_code}")
                print(f"  响应内容: {response.text[:100]}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到服务器，请检查:")
            print(f"  1. 服务器地址是否正确: {self.base_url}")
            print(f"  2. Ollama服务是否启动 (运行 'ollama serve')")
            print(f"  3. 防火墙是否允许11434端口")
            return False
            
        except requests.exceptions.Timeout:
            print(f"❌ 连接超时 (5秒)")
            return False
            
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def send_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Optional[Dict[str, Any]]:
        """
        发送请求到AI服务器
        
        参数:
            endpoint: API端点路径
            data: 请求数据
            method: HTTP方法
            
        返回:
            解析后的响应数据 或 None
        """
        url = f"{self.base_url}{endpoint}"
        print(f"📤 发送请求到: {url}")
        
        if len(str(data)) < 200:
            print(f"  请求数据: {json.dumps(data, ensure_ascii=False)}")
        else:
            print(f"  请求数据: {json.dumps(data, ensure_ascii=False)[:150]}...")
        
        try:
            start_time = time.time()
            
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    json=data,
                    timeout=self.timeout
                )
            else:
                response = self.session.get(
                    url,
                    params=data,
                    timeout=self.timeout
                )
            
            # 记录响应时间
            response_time = time.time() - start_time
            self.last_response_time = response_time
            print(f"📥 响应状态: {response.status_code}")
            print(f"⏱️ 响应时间: {response_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功")
                return result
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"  错误信息: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时 ({self.timeout}秒)")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def generate_text(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        """
        生成文本（Ollama专用）
        
        参数:
            model: 模型名称
            prompt: 提示词
            **kwargs: 额外参数
            
        返回:
            生成的文本
        """
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        # 添加额外参数
        data.update(kwargs)
        
        response = self.send_request("/api/generate", data)
        if response:
            return response.get("response")
        return None
    
    def get_models(self) -> list:
        """
        获取可用的模型列表
        
        返回:
            模型列表
        """
        response = self.send_request("/api/tags", {}, "GET")
        if response and "models" in response:
            return response["models"]
        return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模型信息
        
        参数:
            model_name: 模型名称
            
        返回:
            模型信息
        """
        data = {"name": model_name}
        return self.send_request("/api/show", data)
    
    def close(self):
        """关闭连接"""
        self.session.close()
        print("🔌 AI连接器已关闭")


class OllamaConnector:
    """
    Ollama专用连接器
    包装AIConnector，提供Ollama特定接口
    """
    
    def __init__(self, ip: str = "localhost", port: int = 11434, model: str = None, timeout: int = 60):
        """
        初始化Ollama连接器
        
        参数:
            ip: Ollama服务器IP
            port: Ollama服务器端口
            model: 默认模型名称
            timeout: 超时时间(秒)
        """
        self.ip = ip
        self.port = port
        self.model = model
        self.timeout = timeout
        
        # 创建基础连接器
        base_url = f"http://{ip}:{port}"
        self.connector = AIConnector(base_url=base_url, timeout=timeout)
        
        # 连接状态
        self._is_connected = False
        
        print(f"🔌 Ollama连接器初始化完成")
        print(f"  地址: {ip}:{port}")
        print(f"  模型: {model or '未指定'}")
        print(f"  超时: {timeout}秒")
    
    @property
    def base_url(self) -> str:
        """基础URL"""
        return f"http://{self.ip}:{self.port}"
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._is_connected
    
    def connect(self) -> bool:
        """
        连接到Ollama服务
        
        返回:
            连接是否成功
        """
        print(f"🔌 连接到Ollama服务: {self.base_url}")
        
        success = self.connector.test_connection()
        if success:
            self._is_connected = True
            print(f"✅ Ollama连接成功")
        else:
            self._is_connected = False
            print(f"❌ Ollama连接失败")
        
        return success
    
    def disconnect(self):
        """断开连接"""
        self.connector.close()
        self._is_connected = False
        print("🔌 Ollama连接已断开")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        参数:
            prompt: 提示词
            **kwargs: 额外参数
            
        返回:
            AI生成的文本
        """
        if not self._is_connected:
            return "错误: 未连接到Ollama服务"
        
        if not self.model:
            return "错误: 未设置模型名称"
        
        result = self.connector.generate_text(
            model=self.model,
            prompt=prompt,
            **kwargs
        )
        
        if result:
            return result
        else:
            return "错误: 生成失败，请检查连接和模型"
    
    def check_connection(self) -> bool:
        """
        检查连接状态
        
        返回:
            连接是否正常
        """
        return self.connector.test_connection()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取连接状态信息
        
        返回:
            状态字典
        """
        return {
            "ip": self.ip,
            "port": self.port,
            "model": self.model,
            "connected": self._is_connected,
            "base_url": self.base_url
        }


# 使用示例
if __name__ == "__main__":
    # 测试AIConnector
    print("=" * 50)
    print("测试 AIConnector")
    print("=" * 50)
    
    connector = AIConnector(
        base_url="",
        timeout=30
    )
    
    # 测试连接
    if connector.test_connection():
        print("\n获取模型列表...")
        models = connector.get_models()
        if models:
            print(f"可用模型: {[m.get('name', '未知') for m in models]}")
    
    connector.close()
    
    # 测试OllamaConnector
    print("\n" + "=" * 50)
    print("测试 OllamaConnector")
    print("=" * 50)
    
    ollama = OllamaConnector(
        ip="localhost",
        port=11434,
        model="qwen:7b",
        timeout=30
    )
    
    # 连接测试
    if ollama.connect():
        print(f"连接状态: {ollama.get_status()}")
    
    ollama.disconnect()