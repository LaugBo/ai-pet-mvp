# 局域网AI连接器
# 功能：专门处理局域网内的AI连接，支持Open WebUI和Ollama

import socket
import requests
from typing import List, Dict, Any, Optional
from .connector import AIConnector  # 导入基础连接器

class LocalNetworkConnector(AIConnector):
    """
    局域网AI连接器
    继承自AIConnector，增加局域网特有功能
    """
    
    def __init__(self, ip_address: str = None, port: int = None, ai_type: str = "ollama"):
        """
        初始化局域网连接器
        
        参数:
            ip_address: 局域网IP地址
            port: 端口号
            ai_type: AI类型，支持 "ollama" 或 "openwebui"
        """
        self.ip_address = ip_address or self._detect_local_ip()
        self.port = port or self._get_default_port(ai_type)
        self.ai_type = ai_type
        
        # 根据AI类型构建base_url
        base_url = self._build_base_url()
        
        # 调用父类初始化
        super().__init__(base_url=base_url, timeout=60)
        
        print(f"局域网连接器初始化完成")
        print(f"目标IP: {self.ip_address}")
        print(f"目标端口: {self.port}")
        print(f"AI类型: {self.ai_type}")
    
    def _detect_local_ip(self) -> str:
        """
        自动检测本机局域网IP
        
        返回:
            本机IP地址
        """
        try:
            # 创建一个socket连接到外部地址
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google DNS
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "192.168.1.1"  # 默认IP
    
    def _get_default_port(self, ai_type: str) -> int:
        """
        获取默认端口
        
        参数:
            ai_type: AI类型
            
        返回:
            默认端口号
        """
        default_ports = {
            "ollama": 11434,
            "openwebui": 8080
        }
        return default_ports.get(ai_type.lower(), 11434)
    
    def _build_base_url(self) -> str:
        """
        构建基础URL
        
        返回:
            完整的base_url
        """
        return f"http://{self.ip_address}:{self.port}"
    
    def scan_local_network(self, start_ip: int = 1, end_ip: int = 254) -> List[Dict[str, Any]]:
        """
        扫描局域网，查找可用的AI服务器
        
        参数:
            start_ip: 起始IP段
            end_ip: 结束IP段
            
        返回:
            找到的服务器列表
        """
        print(f"开始扫描局域网 {self.ip_address.rsplit('.', 1)[0]}.{start_ip}-{end_ip}")
        
        found_servers = []
        base_ip = self.ip_address.rsplit('.', 1)[0]  # 获取前三个部分
        
        for i in range(start_ip, end_ip + 1):
            test_ip = f"{base_ip}.{i}"
            
            # 跳过本机
            if test_ip == self.ip_address:
                continue
            
            # 测试两种类型的AI服务器
            for ai_type, port in [("ollama", 11434), ("openwebui", 8080)]:
                test_url = f"http://{test_ip}:{port}"
                
                try:
                    response = requests.get(f"{test_url}/", timeout=2)
                    if response.status_code == 200:
                        server_info = {
                            "ip": test_ip,
                            "port": port,
                            "type": ai_type,
                            "url": test_url
                        }
                        found_servers.append(server_info)
                        print(f"✅ 发现{ai_type}服务器: {test_ip}:{port}")
                        break
                except:
                    continue
        
        print(f"扫描完成，找到 {len(found_servers)} 个服务器")
        return found_servers
    
    def get_ai_info(self) -> Optional[Dict[str, Any]]:
        """
        获取AI服务器信息
        
        返回:
            服务器信息
        """
        endpoints = {
            "ollama": "/api/version",
            "openwebui": "/api/version"  # Open WebUI可能有不同端点
        }
        
        endpoint = endpoints.get(self.ai_type, "/api/version")
        
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                info = response.json()
                info["server_type"] = self.ai_type
                info["address"] = self.base_url
                return info
        except:
            pass
        
        return None
    
    def chat(self, message: str, model: str = "llama3", **kwargs) -> Optional[str]:
        """
        发送聊天消息
        
        参数:
            message: 用户消息
            model: 模型名称
            **kwargs: 其他参数
            
        返回:
            AI的回复
        """
        if self.ai_type == "ollama":
            data = {
                "model": model,
                "prompt": message,
                "stream": False,
                **kwargs
            }
            endpoint = "/api/generate"
        elif self.ai_type == "openwebui":
            data = {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "stream": False,
                **kwargs
            }
            endpoint = "/api/chat/completions"
        else:
            print(f"❌ 不支持的AI类型: {self.ai_type}")
            return None
        
        response = self.send_request(endpoint, data)
        
        if response:
            if self.ai_type == "ollama":
                return response.get("response")
            elif self.ai_type == "openwebui":
                if "choices" in response and len(response["choices"]) > 0:
                    return response["choices"][0]["message"]["content"]
        
        return None

# 使用示例
if __name__ == "__main__":
    # 示例1：连接到Open WebUI
    print("=" * 50)
    print("示例1：连接到Open WebUI")
    print("=" * 50)
    
    webui_connector = LocalNetworkConnector(
        ip_address="192.168.1.13",  # 您的AI主机IP
        port=8080,
        ai_type="openwebui"
    )
    
    if webui_connector.test_connection():
        info = webui_connector.get_ai_info()
        if info:
            print(f"服务器信息: {info}")
        
        # 发送测试消息
        response = webui_connector.chat("你好，请介绍一下你自己", "llama3")
        if response:
            print(f"AI回复: {response}")
    
    webui_connector.close()
    
    # 示例2：扫描局域网
    print("\n" + "=" * 50)
    print("示例2：扫描局域网")
    print("=" * 50)
    
    scanner = LocalNetworkConnector()
    servers = scanner.scan_local_network(1, 20)  # 扫描前20个IP
    
    if servers:
        for server in servers:
            print(f"找到: {server['type']} - {server['url']}")
    else:
        print("未找到任何AI服务器")
    
    scanner.close()