🎯 项目概述

AI宠物MVP​ 是一个具有情感交互能力的AI聊天伙伴桌面应用。它能够与用户对话，根据对话内容分析情感状态，并保存对话历史。

✨ 核心功能

🤖 AI对话​ - 支持与本地Ollama AI模型对话

❤️ 情感系统​ - AI宠物会根据对话内容改变心情

💾 记忆系统​ - 自动保存对话历史和情感记录

🎨 图形界面​ - 使用PyQt5构建的桌面应用

⚙️ 配置管理​ - 可自定义AI设置和应用偏好

📁 项目结构
复制
ai_pet_mvp/
├── data/                          # 数据目录
│   ├── config/                    # 配置文件
│   └── memory/                    # 记忆存储
├── src/                           # 源代码
│   ├── core/                      # 核心模块
│   │   ├── ai/                    # AI模块
│   │   ├── mood/                  # 心情系统
│   │   └── memory/                # 记忆系统
│   ├── ui/                        # 用户界面
│   └── utils/                     # 工具模块
├── venv/                          # Python虚拟环境
├── requirements.txt               # 依赖包列表
├── run_app.py                     # 应用启动脚本
└── README.md                      # 项目说明
🚀 快速开始
环境要求

Python: 3.8 或更高版本

内存: 至少 4GB RAM

磁盘空间: 至少 500MB

可选: Ollama 服务（用于本地AI模型）

安装步骤

克隆项目

bash
复制
git clone https://github.com/你的用户名/ai-pet-mvp.git
cd ai-pet-mvp

创建虚拟环境

bash
复制
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate

安装依赖

bash
复制
pip install -r requirements.txt

安装Ollama（可选）

下载地址: https://ollama.com/

拉取模型: ollama pull qwen:7b

启动应用

bash
复制
python run_app.py
🔧 功能模块
1. AI模块 (src/core/ai/)

适配器模式: 统一AI服务接口

Ollama连接: 支持本地AI模型

错误处理: 连接失败自动重试

状态管理: 监控AI服务连接状态

2. 心情系统 (src/core/mood/)

情感分析: 分析文本情感倾向

心情类型: 6种基本心情（开心、伤心、中性、生气、害怕、困惑）

图片显示: 心情变化伴随图片更新

历史记录: 保存心情变化轨迹

3. 记忆系统 (src/core/memory/)

对话存储: 自动保存所有对话

搜索功能: 按关键词搜索历史对话

摘要生成: 自动生成对话摘要

备份恢复: 支持数据备份和恢复

4. 用户界面 (src/ui/)

主窗口: PyQt5桌面应用框架

聊天界面: 消息气泡式聊天窗口

心情显示: 侧边栏显示AI宠物当前心情

状态栏: 显示连接状态和消息计数

⚠️ 已知Bug和注意事项
🐛 已修复的Bug

✅ 重复参数错误​ - 修复了json.dump()中的重复ensure_ascii参数

✅ 导入缺失​ - 修复了缺少QFrame和Path导入的问题

✅ 方法定义错误​ - 修复了方法定义语法错误

✅ AI连接器​ - 添加了缺失的OllamaConnector类定义

🔴 已知但未修复的问题

测试依赖缺失​ - 测试套件需要pytest-timeout和pytest-html插件

变量命名不一致​ - 测试代码和源代码中的DATA_DIR变量名不一致

网络依赖​ - 需要联网下载部分Python包

Ollama服务依赖​ - 需要本地运行Ollama服务才能使用AI功能

图片资源缺失​ - 心情图片文件需要手动创建

⚡ 性能注意事项

内存使用: 长时间运行可能占用较多内存

启动时间: 首次启动可能需要较长时间加载资源

网络请求: AI对话依赖网络连接

文件IO: 大量对话历史可能影响存储性能

📦 依赖说明
核心依赖
复制
PyQt5>=5.15.0         # GUI界面框架
requests>=2.28.0      # HTTP请求库
pandas>=2.0.0         # 数据处理
jieba>=0.42.1         # 中文分词
开发依赖
复制
pytest>=7.0.0         # 测试框架
pytest-html>=3.0.0    # HTML测试报告
pytest-timeout>=2.0.0 # 测试超时控制
🔄 开发状态
✅ 已完成的功能

[x] 基础项目骨架

[x] AI连接模块

[x] 配置管理系统

[x] 图形用户界面

[x] 记忆存储系统

[x] 情感分析系统

[x] UI集成

[x] 记忆优化功能

🚧 待完善的功能

[ ] 完整的测试套件

[ ] 详细的用户文档

[ ] 性能优化

[ ] 错误处理改进

[ ] 更多心情图片资源

🤔 使用说明
基本使用流程

确保Ollama服务已启动

运行python run_app.py

在输入框中输入消息

按Enter或点击发送按钮

查看AI回复和心情变化

配置说明

AI配置: 编辑data/config/ai_profiles.json

应用设置: 编辑data/config/settings.json

心情规则: 编辑data/config/mood_rules.json

数据管理

对话历史: data/memory/conversations/

心情记录: data/memory/moods/

对话摘要: data/memory/summaries/

🐛 故障排除
常见问题

应用无法启动

检查Python版本是否为3.8+

确保已安装所有依赖: pip install -r requirements.txt

检查虚拟环境是否激活

AI连接失败

确认Ollama服务已运行: ollama serve

检查网络连接

验证ai_profiles.json中的配置

心情图片不显示

确保src/ui/assets/moods/目录存在

目录中应有对应的PNG图片文件

测试运行失败

安装测试依赖: pip install pytest pytest-timeout pytest-html

检查DATA_DIR变量名是否一致

调试模式
bash
复制
python run_app.py --debug
📤 如何上传到GitHub
第一步：准备本地仓库

初始化Git仓库

bash
复制
git init

添加所有文件

bash
复制
git add .

提交初始版本

bash
复制
git commit -m "Initial commit: AI宠物MVP项目"
