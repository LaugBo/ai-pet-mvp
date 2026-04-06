# AI宠物MVP - 开发者指南

欢迎开发者！本文档将帮助你理解AI宠物MVP的架构、扩展方式和开发规范。

## 目录
- [项目架构](#项目架构)
- [代码结构](#代码结构)
- [模块详解](#模块详解)
- [扩展开发](#扩展开发)
- [API参考](#api参考)
- [测试指南](#测试指南)
- [贡献指南](#贡献指南)
- [发布流程](#发布流程)

## 项目架构

### 整体架构
┌─────────────────────────────────────────────────────────────┐

│                     用户界面层 (UI Layer)                    │

│  ┌──────────────────────────────────────────────────────┐  │

│  │                  PyQt5 GUI 应用程序                    │  │

│  │  • MainWindow: 主窗口                                 │  │

│  │  • ChatManager: 聊天管理                              │  │

│  │  • MoodDisplay: 心情显示                              │  │

│  └──────────────────────────────────────────────────────┘  │

│                              │                              │

│  ┌──────────────────────────────────────────────────────┐  │

│  │                业务逻辑层 (Business Logic)             │  │

│  │  • AIManager: AI交互管理                              │  │

│  │  • MoodManager: 心情管理                              │  │

│  │  • MemoryManager: 记忆管理                            │  │

│  └──────────────────────────────────────────────────────┘  │

│                              │                              │

│  ┌──────────────────────────────────────────────────────┐  │

│  │                数据访问层 (Data Access)                │  │

│  │  • ConfigManager: 配置管理                            │  │

│  │  • MemoryStorage: 记忆存储                            │  │

│  │  • FileManager: 文件管理                              │  │

│  └──────────────────────────────────────────────────────┘  │

│                              │                              │

│  ┌──────────────────────────────────────────────────────┐  │

│  │                外部服务层 (External Services)          │  │

│  │  • Ollama API: AI模型服务                             │  │

│  │  • (未来) OpenAI API, Claude API, 等                  │  │

│  └──────────────────────────────────────────────────────┘  │

└─────────────────────────────────────────────────────────────┘
### 设计模式
- **适配器模式**: AI服务适配器 (`AIAdapter`)
- **观察者模式**: 信号/槽机制 (`PyQt5 signals`)
- **单例模式**: 配置管理、日志管理
- **工厂模式**: AI适配器创建
- **策略模式**: 心情分析策略

### 数据流
用户输入 → 主窗口 → 聊天管理器 → AI管理器 → AI服务

↓          ↓           ↓           ↓

心情分析 ← 心情管理器 ← 响应处理 ← 响应接收

↓

心情显示 → 记忆存储 → 对话保存
## 代码结构

### 项目根目录
ai_pet_mvp/

├── data/                    # 数据目录

│   ├── config/             # 配置文件

│   └── memory/             # 记忆数据

├── src/                    # 源代码

│   ├── core/              # 核心模块

│   │   ├── ai/           # AI相关

│   │   ├── mood/         # 心情系统

│   │   └── memory/       # 记忆系统

│   ├── ui/               # 用户界面

│   └── utils/            # 工具模块

├── tests/                 # 测试代码

├── scripts/              # 工具脚本

├── docs/                 # 文档

├── examples/             # 示例代码

├── logs/                 # 日志文件

└── backups/              # 备份文件
### 核心模块说明

#### 1. AI模块 (`src/core/ai/`)

AI适配器接口

class AIAdapter:

def connect() -> bool

def disconnect()

def generate(prompt: str) -> str

Ollama适配器

class OllamaConnector(AIAdapter):

def init(ip, port, model)

AI管理器

class AIManager:

def init(config)

def connect() -> bool

def generate_response(prompt) -> str
#### 2. 心情模块 (`src/core/mood/`)

心情分析器

class MoodAnalyzer:

def analyze(text) -> MoodResult

心情管理器

class MoodManager:

def analyze_and_update(text) -> bool

def register_callback(callback)

心情结果

@dataclass

class MoodResult:

mood_type: MoodType

confidence: float

reason: str
#### 3. 记忆模块 (`src/core/memory/`)

记忆存储

class MemoryStorage:

def save_conversation(data) -> bool

def load_conversation(filename) -> dict

记忆读取

class MemoryRecall:

def search_conversations(query) -> list

记忆优化

class MemoryOptimizer:

def generate_summary(filename) -> dict
#### 4. UI模块 (`src/ui/`)
主窗口

class MainWindow(QMainWindow):

def init(config, mood, image)

def update_ai_response(text)

聊天管理器

class ChatManager(QObject):

signal response_received(str)

signal error_occurred(str)

def send_message(text)
#### 5. 工具模块 (`src/utils/`)
配置管理

class ConfigManager:

def load_config(filename) -> dict

def save_config(filename, data) -> bool

日志系统

class AIPetLogger:

def info(msg, **kwargs)

def error(msg, **kwargs)

错误处理

class ErrorHandler:

def handle_error(error) -> AIError
## 模块详解

### AI适配器系统

#### 适配器接口
class AIAdapter(ABC):

"""AI适配器抽象基类"""
@abstractmethod
def connect(self) -> bool:
    """连接AI服务"""
    pass

@abstractmethod
def disconnect(self):
    """断开连接"""
    pass

@abstractmethod
def generate(self, prompt: str, **kwargs) -> str:
    """生成响应"""
    pass
    #### 添加新的AI适配器
1. 创建新适配器类
2. 实现抽象方法
3. 在工厂中注册
4. 更新配置文件

示例：添加OpenAI适配器
src/core/ai/openai_adapter.py

class OpenAIAdapter(AIAdapter):

def init(self, api_key: str, model: str = "gpt-3.5-turbo"):

self.api_key = api_key

self.model = model

self.client = None
def connect(self) -> bool:
    try:
        import openai
        self.client = openai.OpenAI(api_key=self.api_key)
        return True
    except Exception as e:
        return False

def generate(self, prompt: str) -> str:
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
    ### 心情分析系统
### 心情分析系统

#### 分析流程
文本预处理

↓

关键词提取 (jieba分词)

↓

情感分析 (规则匹配)

↓

主题检测

↓

置信度计算

↓

生成结果
#### 自定义心情规则
编辑 `data/config/mood_rules.json`:
json

{

"moods": {

"excited": {

"keywords": ["激动", "兴奋", "太棒了", "哇塞"],

"weight": 1.2,

"decay_rate": 0.8

},

"calm": {

"keywords": ["平静", "安宁", "放松", "舒缓"],

"weight": 0.8,

"decay_rate": 0.9

}

}

}
### 记忆系统

#### 存储格式
json

{

"conversations": {

"20240101_120000.json": {

"user": "你好",

"ai": "你好！",

"timestamp": "2024-01-01T12:00:00",

"mood": "happy",

"metadata": {

"tokens": 20,

"duration": 1.5

}

}

},

"summaries": {

"20240101.json": {

"content": "上午的对话...",

"keywords": ["问候", "介绍"],

"summary": "用户和AI互相问候"

}

}

}
#### 数据备份
- 自动备份: 每天一次
- 手动备份: `python scripts/backup.py create`
- 恢复备份: `python scripts/backup.py restore <name>`

## 扩展开发

### 添加新功能模块

#### 1. 创建模块结构
src/core/new_feature/

├── init.py

├── manager.py      # 功能管理器

├── storage.py      # 数据存储

└── analyzer.py     # 业务逻辑
#### 2. 实现基本类
src/core/new_feature/manager.py

from src.utils.logger import get_logger

from src.utils.error_handler import safe_call

class NewFeatureManager:

def init(self, config=None):

self.logger = get_logger("new_feature")

self.config = config or {}
@safe_call(operation="执行功能")
def execute(self, data):
    # 实现功能逻辑
    pass
#### 3. 集成到主应用
在 run_app.py 中添加

from src.core.new_feature.manager import NewFeatureManager

创建实例

feature_manager = NewFeatureManager()

集成到窗口

window.set_feature_manager(feature_manager)
### 创建新的心情类型

#### 1. 扩展MoodType枚举
src/core/mood/manager.py

class MoodType(Enum):

EXCITED = "excited"      # 新增

CALM = "calm"           # 新增

HAPPY = "happy"

SAD = "sad"

# ...
#### 2. 添加分析规则
在 mood_rules.json 中添加

"excited": {

"keywords": ["激动", "兴奋", "惊喜"],

"weight": 1.2

}
#### 3. 添加心情图片
- 创建 `src/ui/assets/moods/excited.png`
- 图片尺寸: 200x200像素
- 格式: PNG透明背景

### 添加新的AI服务

#### 1. 创建适配器
src/core/ai/new_adapter.py

class NewAIAdapter(AIAdapter):

def init(self, **config):

self.config = config
 
 def connect(self):
    # 实现连接逻辑
    pass

def generate(self, prompt):
    # 实现生成逻辑
    pass
#### 2. 注册到工厂
src/core/ai/adapter.py

class AIAdapter:

@staticmethod

def create_adapter(config):

adapter_type = config.get("adapter_type")
if adapter_type == "new_service":  # 新增
    from .new_adapter import NewAIAdapter
    return NewAIAdapter(**config)
# ...
#### 3. 更新配置文件
json

{

"adapter_type": "new_service",

"api_key": "your-api-key",

"endpoint": "https://api.newservice.com
"

}
## API参考

### 核心类API

#### AIManager
class AIManager:

"""AI管理器"""
def __init__(self, config: dict):
    """
    初始化AI管理器
    
    Args:
        config: AI配置字典
            - adapter_type: 适配器类型
            - ip: AI服务IP
            - port: AI服务端口
            - model: 模型名称
    """

def connect(self) -> bool:
    """连接到AI服务"""

def disconnect(self):
    """断开连接"""

def generate_response(self, prompt: str, **kwargs) -> str:
    """
    生成AI响应
    
    Args:
        prompt: 用户输入
        **kwargs: 额外参数
        
    Returns:
        AI响应文本
    """

def get_status(self) -> dict:
    """获取AI状态"""
 #### MoodManager
 class MoodManager:

"""心情管理器"""
def __init__(self, storage_manager=None):
    """
    初始化心情管理器
    
    Args:
        storage_manager: 记忆存储管理器
    """

def analyze_and_update(self, text: str) -> bool:
    """
    分析文本并更新心情
    
    Args:
        text: 要分析的文本
        
    Returns:
        是否成功更新
    """

def register_mood_change_callback(self, callback: Callable):
    """
    注册心情变化回调
    
    Args:
        callback: 回调函数
            签名: def callback(old_mood: MoodType, new_result: MoodResult)
    """

def get_mood_stats(self) -> dict:
    """获取心情统计"""
 #### MemoryStorage
 class MemoryStorage:

"""记忆存储"""
def __init__(self, base_dir=None):
    """
    初始化记忆存储
    
    Args:
        base_dir: 基础目录，默认为data/memory
    """

def save_conversation(self, data: dict, filename=None) -> bool:
    """
    保存对话
    
    Args:
        data: 对话数据
        filename: 文件名，默认为时间戳
        
    Returns:
        是否保存成功
    """

def get_recent_conversations(self, limit: int = 10) -> list:
    """
    获取最近的对话
    
    Args:
        limit: 最大数量
        
    Returns:
        对话列表
    """

def search_conversations(self, query: str) -> list:
    """搜索对话"""
    ### 工具类API

#### 配置管理
from src.utils.config import get_config_manager

config_manager = get_config_manager()

加载配置

config = config_manager.load_config("settings.json")

保存配置

config_manager.save_config("settings.json", new_config)
#### 日志系统
from src.utils.logger import get_logger, info, error

logger = get_logger("module_name")

记录日志

logger.info("操作完成", user="test", action="login")

logger.error("操作失败", error=str(e))

快捷函数

info("信息消息")

error("错误消息")
#### 错误处理
from src.utils.error_handler import safe_call, AIError, ErrorCode

@safe_call(operation="重要操作", default_return=None)

def risky_operation():

# 自动处理异常

pass

手动处理

try:

# 可能失败的操作

pass

except Exception as e:

raise AIError(

error_code=ErrorCode.NETWORK_ERROR,

message="操作失败",

original_error=e

)
## 测试指南

### 运行测试
bash

运行所有测试

python run_tests.py run

运行核心模块测试

python run_tests.py run core

运行单个测试文件

python run_tests.py single test_core/test_ai_adapter.py

生成覆盖率报告

python run_tests.py run all --coverage

运行完整测试套件

python run_tests.py suite
### 测试目录结构
tests/

├── conftest.py              # 测试配置

├── test_core/              # 核心模块测试

├── test_ui/                # UI模块测试

├── test_utils/             # 工具模块测试

└── test_integration/       # 集成测试
### 编写测试
import pytest

from unittest.mock import Mock, patch

def test_ai_manager_connection():

"""测试AI管理器连接"""
# 模拟依赖
mock_adapter = Mock()
mock_adapter.connect.return_value = True

with patch('src.core.ai.adapter.AIAdapter.create_adapter') as mock_create:
    mock_create.return_value = mock_adapter
    
    # 创建测试对象
    ai_manager = AIManager({"adapter_type": "test"})
    
    # 执行测试
    result = ai_manager.connect()
    
    # 验证结果
    assert result is True
    assert ai_manager.is_connected is True
    ### 测试最佳实践
1. **单元测试**: 每个函数都有测试
2. **集成测试**: 模块间交互测试
3. **性能测试**: 响应时间、内存使用
4. **边界测试**: 异常情况处理
5. **模拟外部依赖**: 使用unittest.mock

## 贡献指南

### 开发流程
1. Fork仓库
2. 创建特性分支
3. 编写代码和测试
4. 运行测试
5. 提交Pull Request
6. 代码审查
7. 合并到主分支

### 代码规范
- **PEP 8**: Python代码规范
- **类型注解**: 使用type hints
- **文档字符串**: 所有函数和类
- **命名规范**:
  - 类名: `CamelCase`
  - 函数名: `snake_case`
  - 常量: `UPPER_CASE`
  - 私有成员: `_private`

### 提交信息规范
类型(范围): 简短描述

详细描述（可选）

功能变更1

功能变更2

修复 #123
**类型**: feat, fix, docs, style, refactor, test, chore
**范围**: ai, mood, memory, ui, config, etc.

示例:
feat(ai): 添加OpenAI适配器支持

添加OpenAIAdapter类

更新AI适配器工厂

添加OpenAI配置示例

新增功能，不破坏现有API
### 代码审查标准
1. 功能正确性
2. 代码质量
3. 测试覆盖率
4. 文档完整性
5. 性能影响
6. 向后兼容性

## 发布流程

### 版本管理
- **主版本**: 重大变更，不向后兼容
- **次版本**: 新功能，向后兼容
- **修订版本**: Bug修复，向后兼容

### 发布步骤
1. 更新版本号
2. 更新CHANGELOG.md
3. 运行完整测试
4. 构建发布包
5. 创建GitHub Release
6. 更新文档
7. 发布公告

### 构建脚本
bash

创建发布包

python setup.py sdist bdist_wheel

检查包

twine check dist/*

上传到PyPI

twine upload dist/*
### 发布检查清单
- [ ] 所有测试通过
- [ ] 文档更新完成
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] 依赖项已检查
- [ ] 发布说明已编写
- [ ] 标签已创建
- [ ] 发布包已构建

---

## 附录

### 开发环境设置
bash

克隆仓库

git clone https://github.com/yourusername/ai-pet-mvp.git

cd ai-pet-mvp

创建虚拟环境

python -m venv venv

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate     # Windows

安装依赖

pip install -r requirements.txt

pip install -r requirements-dev.txt

安装开发工具

pre-commit install
### 常用命令
bash

代码质量

flake8 src/                    # 代码检查

black src/                     # 代码格式化

isort src/                     # 导入排序

mypy src/                      # 类型检查

文档

pdoc src --html --output-dir docs/api  # 生成API文档

依赖管理

pip freeze > requirements.txt          # 冻结依赖

pip-compile requirements.in            # 编译依赖
### 调试技巧
python

启用调试日志

import logging

logging.basicConfig(level=logging.DEBUG)

使用pdb调试

import pdb; pdb.set_trace()

性能分析

import cProfile

cProfile.run('my_function()')
### 性能优化建议
1. 使用缓存减少重复计算
2. 异步处理耗时操作
3. 批量读写文件
4. 使用生成器处理大数据
5. 优化数据库查询
6. 内存泄漏检测

---

希望这份开发者指南能帮助你更好地理解和开发AI宠物MVP项目。如果有任何问题，请查看API文档或提交Issue。

Happy coding! 🚀
