# 配置管理器
# 功能：统一管理所有配置文件，支持多级配置覆盖

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class ConfigManager:
    """
    配置管理器
    负责加载、管理和保存所有配置
    """
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置管理器
        
        参数:
            config_dir: 配置文件目录，默认为 data/config/
        """
        if config_dir is None:
            # 默认配置文件目录
            self.config_dir = Path(__file__).parent.parent.parent / "data" / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置缓存
        self._config_cache = {}
        
        print(f"配置管理器初始化完成")
        print(f"配置目录: {self.config_dir}")
    
    def load_config(self, filename: str, create_if_not_exist: bool = False) -> Dict[str, Any]:
        """
        加载配置文件
        
        参数:
            filename: 配置文件名（如 settings.json）
            create_if_not_exist: 如果文件不存在，是否创建
            
        返回:
            配置字典
        """
        config_path = self.config_dir / filename
        
        # 检查文件是否存在
        if not config_path.exists():
            if create_if_not_exist:
                print(f"配置文件不存在，创建默认: {config_path}")
                default_config = self._get_default_config(filename)
                self.save_config(filename, default_config)
                return default_config
            else:
                print(f"配置文件不存在: {config_path}")
                return {}
        
        try:
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 缓存配置
            self._config_cache[filename] = config
            
            print(f"加载配置文件: {filename}")
            return config
            
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {filename} - {e}")
            return {}
        except Exception as e:
            print(f"加载配置文件失败: {filename} - {e}")
            return {}
    
    def save_config(self, filename: str, config: Dict[str, Any]) -> bool:
        """
        保存配置文件
        
        参数:
            filename: 配置文件名
            config: 配置字典
            
        返回:
            是否保存成功
        """
        config_path = self.config_dir / filename
        
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新缓存
            self._config_cache[filename] = config
            
            print(f"保存配置文件: {filename}")
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {filename} - {e}")
            return False
    
    def get_config_value(self, 
                        config_name: str, 
                        key_path: str, 
                        default_value: Any = None) -> Any:
        """
        获取配置值（支持点分隔的路径）
        
        参数:
            config_name: 配置文件名
            key_path: 键路径，如 "ai.connection.timeout"
            default_value: 默认值
            
        返回:
            配置值
        """
        # 加载或获取缓存配置
        if config_name not in self._config_cache:
            config = self.load_config(config_name)
            if not config:
                return default_value
            self._config_cache[config_name] = config
        
        config = self._config_cache[config_name]
        
        # 分割键路径
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default_value
            return value
        except Exception:
            return default_value
    
    def set_config_value(self, 
                        config_name: str, 
                        key_path: str, 
                        value: Any) -> bool:
        """
        设置配置值（支持点分隔的路径）
        
        参数:
            config_name: 配置文件名
            key_path: 键路径
            value: 要设置的值
            
        返回:
            是否设置成功
        """
        # 确保配置已加载
        if config_name not in self._config_cache:
            config = self.load_config(config_name, create_if_not_exist=True)
            if not config:
                config = {}
            self._config_cache[config_name] = config
        
        config = self._config_cache[config_name]
        keys = key_path.split('.')
        
        # 遍历路径，创建嵌套字典
        current_dict = config
        for i, key in enumerate(keys[:-1]):
            if key not in current_dict:
                current_dict[key] = {}
            if not isinstance(current_dict[key], dict):
                current_dict[key] = {}
            current_dict = current_dict[key]
        
        # 设置值
        last_key = keys[-1]
        current_dict[last_key] = value
        
        # 保存配置
        return self.save_config(config_name, config)
    
    def _get_default_config(self, filename: str) -> Dict[str, Any]:
        """
        获取默认配置
        
        参数:
            filename: 配置文件名
            
        返回:
            默认配置字典
        """
        default_configs = {
            "settings.json": {
                "app": {
                    "name": "AI宠物MVP",
                    "version": "1.0.0",
                    "author": "Your Name"
                },
                "ui": {
                    "theme": "light",
                    "language": "zh-CN",
                    "window_width": 800,
                    "window_height": 600
                },
                "memory": {
                    "max_history": 100,
                    "auto_save": True,
                    "save_interval": 300
                }
            },
            "mood_rules.json": {
                "moods": {
                    "happy": {
                        "keywords": ["开心", "高兴", "快乐", "哈哈", "太好了"],
                        "priority": 1,
                        "default_image": "happy/default.png"
                    },
                    "excited": {
                        "keywords": ["兴奋", "激动", "惊喜", "哇", "太棒了"],
                        "priority": 2,
                        "default_image": "excited/default.png"
                    },
                    "sad": {
                        "keywords": ["难过", "伤心", "哭", "唉", "失望"],
                        "priority": 3,
                        "default_image": "sad/default.png"
                    },
                    "proud": {
                        "keywords": ["自豪", "骄傲", "成就", "优秀", "成功"],
                        "priority": 4,
                        "default_image": "proud/default.png"
                    },
                    "confused": {
                        "keywords": ["困惑", "疑惑", "不明白", "为什么", "怎么"],
                        "priority": 5,
                        "default_image": "confused/default.png"
                    }
                },
                "default_mood": "happy",
                "mood_change_delay": 3
            },
            "ai_settings.json": {
                "connections": {
                    "openwebui": {
                        "url": "http://localhost:8080",
                        "api_key": "",
                        "timeout": 60
                    },
                    "ollama": {
                        "url": "http://localhost:11434",
                        "timeout": 30
                    }
                },
                "default_model": "llama3",
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        return default_configs.get(filename, {})
    
    # ================== 新增功能：AI配置管理 ==================
    
    def load_ai_profile(self, profile_name: str = None) -> Dict[str, Any]:
        """
        加载AI配置profile
        
        参数:
            profile_name: 配置名称，默认使用active_profile
            
        返回:
            AI配置字典
        """
        # 1. 加载ai_profiles.json
        ai_config = self.load_config("ai_profiles.json")
        
        if not ai_config:
            return {}
        
        # 2. 确定要使用的profile
        if profile_name is None:
            profile_name = ai_config.get("active_profile", "my_openwebui")
        
        profiles = ai_config.get("profiles", {})
        
        if profile_name not in profiles:
            print(f"⚠ AI配置 {profile_name} 不存在，使用第一个可用配置")
            if profiles:
                profile_name = list(profiles.keys())[0]
            else:
                return {}
        
        # 3. 获取profile配置
        profile = profiles[profile_name]
        
        # 4. 添加全局连接设置
        connection_settings = ai_config.get("connection_settings", {})
        default_parameters = ai_config.get("default_parameters", {})
        
        return {
            "profile_name": profile_name,
            "profile": profile,
            "connection_settings": connection_settings,
            "default_parameters": default_parameters
        }
    
    def get_ai_profiles(self) -> List[str]:
        """
        获取所有可用的AI配置名称
        
        返回:
            AI配置名称列表
        """
        ai_config = self.load_config("ai_profiles.json")
        
        if not ai_config:
            return []
        
        profiles = ai_config.get("profiles", {})
        return list(profiles.keys())
    
    def get_active_ai_profile_name(self) -> str:
        """
        获取当前激活的AI配置名称
        
        返回:
            激活的AI配置名称
        """
        ai_config = self.load_config("ai_profiles.json")
        
        if not ai_config:
            return "my_openwebui"
        
        return ai_config.get("active_profile", "my_openwebui")
    
    def set_active_ai_profile(self, profile_name: str) -> bool:
        """
        设置激活的AI配置
        
        参数:
            profile_name: AI配置名称
            
        返回:
            是否设置成功
        """
        ai_config = self.load_config("ai_profiles.json")
        
        if not ai_config:
            return False
        
        profiles = ai_config.get("profiles", {})
        
        if profile_name not in profiles:
            print(f"⚠ AI配置 {profile_name} 不存在")
            return False
        
        ai_config["active_profile"] = profile_name
        return self.save_config("ai_profiles.json", ai_config)
    
    def get_ai_connection_config(self) -> Dict[str, Any]:
        """
        获取当前AI连接的完整配置（最常用的方法）
        
        返回:
            AI连接配置字典
        """
        # 1. 获取当前激活的AI配置
        ai_profile_data = self.load_ai_profile()
        
        if not ai_profile_data:
            return {}
        
        profile_name = ai_profile_data["profile_name"]
        profile = ai_profile_data["profile"]
        connection_settings = ai_profile_data["connection_settings"]
        default_parameters = ai_profile_data["default_parameters"]
        
        # 2. 获取adapter_type
        adapter_type = profile.get("adapter_type", "openwebui")
        
        # 3. 构建base_url
        if "base_url" in profile:
            base_url = profile["base_url"]
        elif "ip_address" in profile and "port" in profile:
            ip_address = profile["ip_address"]
            port = profile["port"]
            base_url = f"http://{ip_address}:{port}"
        else:
            base_url = ""
        
        # 4. 返回完整配置
        return {
            "profile_name": profile_name,
            "adapter_type": adapter_type,
            "base_url": base_url,
            "api_endpoint": profile.get("api_endpoint", ""),
            "api_key": profile.get("api_key", ""),
            "model": profile.get("model", "llama3"),
            "timeout": profile.get("timeout", 60),
            "headers": profile.get("headers", {}),
            "parameters": {
                **default_parameters,
                **profile.get("parameters", {})
            },
            "connection_settings": connection_settings
        }

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """
    获取全局配置管理器实例（单例模式）
    
    返回:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# 新增全局辅助函数
def get_ai_connection_config() -> Dict[str, Any]:
    """
    获取AI连接配置的便捷函数
    
    返回:
        AI连接配置字典
    """
    config_mgr = get_config_manager()
    return config_mgr.get_ai_connection_config()

def get_available_ai_profiles() -> List[str]:
    """
    获取所有可用AI配置名称的便捷函数
    
    返回:
        AI配置名称列表
    """
    config_mgr = get_config_manager()
    return config_mgr.get_ai_profiles()

# 使用示例
if __name__ == "__main__":
    print("配置管理器测试")
    print("=" * 50)
    
    # 创建配置管理器
    config_mgr = get_config_manager()
    
    # 测试加载配置
    settings = config_mgr.load_config("settings.json", create_if_not_exist=True)
    print(f"settings.json: {json.dumps(settings, indent=2, ensure_ascii=False)}")
    
    # 测试获取配置值
    app_name = config_mgr.get_config_value("settings.json", "app.name")
    print(f"应用名称: {app_name}")
    
    # 测试设置配置值
    config_mgr.set_config_value("settings.json", "ui.window_width", 1024)
    
    # 测试保存
    config_mgr.save_config("test_config.json", {"test": "value"})
    
    # 测试新增的AI配置功能
    print("\n" + "=" * 50)
    print("测试AI配置功能")
    print("=" * 50)
    
    # 加载AI配置
    ai_config = config_mgr.get_ai_connection_config()
    if ai_config:
        print(f"当前AI配置名称: {ai_config.get('profile_name', '未知')}")
        print(f"适配器类型: {ai_config.get('adapter_type', '未知')}")
        print(f"基础URL: {ai_config.get('base_url', '未知')}")
        print(f"模型: {ai_config.get('model', '未知')}")
    
    # 获取所有可用配置
    profiles = config_mgr.get_ai_profiles()
    print(f"可用的AI配置: {profiles}")
    
    # 获取当前激活的配置
    active_profile = config_mgr.get_active_ai_profile_name()
    print(f"当前激活的配置: {active_profile}")
    
    # 测试便捷函数
    print("\n使用便捷函数:")
    ai_config2 = get_ai_connection_config()
    print(f"AI连接配置: {ai_config2.get('profile_name', '未知')}")
    
    print("=" * 50)
    print("配置管理器测试完成")