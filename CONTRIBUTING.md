# 贡献指南

欢迎参与AI宠物MVP项目！本指南将帮助你了解如何为项目做出贡献。

## 目录
- [行为准则](#行为准则)
- [如何开始](#如何开始)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试要求](#测试要求)
- [文档要求](#文档要求)
- [问题反馈](#问题反馈)
- [功能建议](#功能建议)
- [发布流程](#发布流程)
- [致谢](#致谢)

## 行为准则

### 我们的承诺
我们致力于为所有贡献者创造一个开放、欢迎、多元、包容、健康的环境。

### 我们的标准
积极的贡献行为包括：
- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表现出同理心

不可接受的行为包括：
- 性暗示的语言或图像
- 挑衅、侮辱/贬损的评论
- 公开或私人的骚扰
- 未经明确许可发布他人的私人信息
- 其他不专业或不合适的行为

### 执行责任
项目维护者有责任明确可接受的行为标准，并对任何不可接受的行为采取适当和公平的纠正措施。

### 适用范围
本行为准则适用于所有项目空间，也适用于个人在公共空间代表项目时的行为。

## 如何开始

### 1. Fork仓库
1. 访问 [GitHub仓库](https://github.com/LaugBo/ai-pet-mvp)
2. 点击右上角的 "Fork" 按钮
3. 选择你的账户

### 2. 克隆代码
bash

克隆你的fork
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

添加上游仓库
git remote add upstream https://github.com/original/ai-pet-mvp.git

复制
### 3. 设置开发环境
bash

创建虚拟环境
python -m venv venv

激活虚拟环境
Linux/macOS
source venv/bin/activate

Windows
venv\Scripts\activate

安装依赖
pip install -r requirements.txt

pip install -r requirements-dev.txt

安装预提交钩子
pre-commit install

复制
### 4. 创建分支
bash

同步最新代码
git fetch upstream

git checkout main

git merge upstream/main

创建特性分支
git checkout -b feat/your-feature-name

或修复分支
git checkout -b fix/issue-number-description

复制
## 开发流程

### 1. 理解项目结构
ai_pet_mvp/

├── src/                    # 源代码

│   ├── core/             # 核心模块

│   ├── ui/               # 用户界面

│   └── utils/            # 工具模块

├── tests/                # 测试代码

├── docs/                 # 文档

├── examples/             # 示例代码

└── scripts/              # 工具脚本

复制
### 2. 开发新功能
1. 在本地测试你的更改
2. 添加或更新测试用例
3. 更新相关文档
4. 确保代码符合规范

### 3. 提交更改
bash

添加更改
git add .

提交（使用规范格式）
git commit -m "feat(module): description of changes"

推送到你的fork
git push origin your-branch-name

复制
### 4. 创建Pull Request
1. 访问你的GitHub仓库
2. 点击 "Compare & pull request"
3. 填写PR模板
4. 等待代码审查

## 代码规范

### Python代码规范
我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范。

#### 自动检查工具
bash

代码格式检查
flake8 src/

代码格式化
black src/

导入排序
isort src/

类型检查
mypy src/

复制
#### 命名规范
- **类名**: `CamelCase`
- **函数名**: `snake_case`
- **变量名**: `snake_case`
- **常量**: `UPPER_CASE`
- **私有成员**: `_private`
- **特殊方法**: `__special__`

#### 类型注解
所有函数和方法都应包含类型注解：
python

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:

"""处理数据函数"""

pass

复制
#### 文档字符串
所有公共函数、类和方法都应包含文档字符串：
python

def calculate_sum(numbers: List[float]) -> float:

"""

计算数字列表的总和

复制
Args:
    numbers: 数字列表
    
Returns:
    所有数字的总和
    
Raises:
    ValueError: 如果列表为空
"""
if not numbers:
    raise ValueError("数字列表不能为空")
return sum(numbers)
复制
### 模块组织规范
1. 每个模块应该有清晰的单一职责
2. 避免循环导入
3. 合理使用 `__init__.py`
4. 模块之间通过接口交互

## 提交规范

### 提交信息格式
类型(范围): 简短描述

详细描述（可选）

功能变更1

功能变更2

修复 #123

复制
### 类型说明
| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(ai): 添加OpenAI适配器` |
| fix | 错误修复 | `fix(memory): 修复数据损坏问题` |
| docs | 文档更新 | `docs(api): 更新API文档` |
| style | 代码格式 | `style(core): 修复代码格式` |
| refactor | 代码重构 | `refactor(ui): 重构窗口类` |
| test | 测试相关 | `test(mood): 添加心情分析测试` |
| chore | 构建/工具 | `chore(deps): 更新依赖版本` |

### 范围说明
范围应该是受影响的模块或组件：
- `ai`: AI相关模块
- `mood`: 心情系统
- `memory`: 记忆系统
- `ui`: 用户界面
- `config`: 配置管理
- `utils`: 工具模块
- `deps`: 依赖管理
- `ci`: 持续集成

### 示例
feat(ai): 添加Claude API支持

添加ClaudeAdapter类

更新AI适配器工厂

添加Claude配置示例

更新相关文档

新增功能，完全向后兼容

复制
## 测试要求

### 测试覆盖率
- 新代码应有相应的测试
- 整体覆盖率不低于80%
- 关键功能覆盖率100%

### 运行测试
bash

运行所有测试
python run_tests.py suite

运行特定模块测试
python run_tests.py run core

运行单个测试文件
python run_tests.py single tests/test_core/test_ai_adapter.py

生成覆盖率报告
python run_tests.py run all --coverage

复制
### 编写测试
python

import pytest

from unittest.mock import Mock, patch

def test_function_success():

"""测试函数成功情况"""

# 准备测试数据

# 执行测试

# 验证结果

def test_function_failure():

"""测试函数失败情况"""

with pytest.raises(ValueError):

# 应该抛出异常的代码

def test_with_mocks():

"""使用模拟对象测试"""

with patch('module.function') as mock_func:

mock_func.return_value = "mocked"

# 执行测试

复制
## 文档要求

### 文档类型
1. **用户文档**: 面向最终用户
2. **开发者文档**: 面向开发者
3. **API文档**: 面向API使用者
4. **部署文档**: 面向系统管理员

### 文档位置
docs/

├── user_guide.md          # 用户指南

├── developer_guide.md     # 开发者指南

├── api_reference.md       # API参考

└── deployment_guide.md    # 部署指南

复制
### 文档标准
1. 使用Markdown格式
2. 包含清晰的目录结构
3. 代码示例可运行
4. 及时更新，与代码同步
5. 中英双语（优先中文）

## 问题反馈

### 报告Bug
1. 在GitHub Issues中搜索是否已存在
2. 创建新的Issue
3. 使用Bug报告模板
4. 提供详细信息

**Bug报告模板:**
markdown

问题描述
清晰描述问题

重现步骤
步骤1

步骤2

步骤3

预期行为
应该发生什么

实际行为
实际发生了什么

环境信息
操作系统: [如: Windows 10]

Python版本: [如: 3.9.0]

项目版本: [如: v1.0.0]

AI服务: [如: Ollama 0.1.0]

日志输出
复制
相关日志
截图/录屏
如果有，请提供

复制
### 讨论功能
1. 在GitHub Discussions中讨论
2. 提出详细的功能描述
3. 讨论实现方案
4. 评估影响范围

## 功能建议

### 提案流程
1. **讨论阶段**: 在Discussions中讨论
2. **设计阶段**: 编写详细设计文档
3. **实现阶段**: 编写代码和测试
4. **审查阶段**: 代码审查和测试
5. **合并阶段**: 合并到主分支

### 设计文档模板
markdown

功能提案: [功能名称]
概述
简要描述功能

问题描述
当前存在的问题或需求

解决方案
提议的解决方案

详细设计
架构变更
接口设计
数据模型
用户界面
实现计划
阶段1: [描述]
阶段2: [描述]
阶段3: [描述]
影响评估
对现有功能的影响
性能影响
向后兼容性
测试计划
单元测试
集成测试
性能测试
文档更新
用户文档
开发者文档
API文档
备选方案
其他可能的解决方案和优缺点

复制
## 发布流程

### 版本规范
我们使用[语义化版本](https://semver.org/lang/zh-CN/):
- **主版本号**: 重大变更，不向后兼容
- **次版本号**: 新功能，向后兼容
- **修订号**: Bug修复，向后兼容

### 发布检查清单
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG已更新
- [ ] 版本号已更新
- [ ] 发布说明已编写
- [ ] 代码已签名
- [ ] 发布包已构建
- [ ] 标签已创建

### 发布步骤
bash

1. 更新版本号
在 init.py 中更新版本
2. 更新CHANGELOG
添加新版本的变更记录
3. 提交发布提交
git commit -m "chore(release): v1.0.0"

4. 创建标签
git tag -a v1.0.0 -m "Release v1.0.0"

5. 推送标签
git push origin v1.0.0

6. 创建GitHub Release
在GitHub上创建Release，包含发布说明
复制
## 致谢

### 贡献者名单
我们感谢所有为项目做出贡献的人！贡献者名单会自动更新在README.md中。

### 特殊贡献
- **代码贡献**: 实现新功能、修复bug
- **文档贡献**: 编写和更新文档
- **测试贡献**: 编写测试用例
- **问题反馈**: 报告bug和建议功能
- **代码审查**: 审查Pull Request
- **社区支持**: 帮助其他用户

### 成为维护者
如果你长期积极贡献，并希望成为项目维护者：
1. 展示对项目的深刻理解
2. 持续做出高质量贡献
3. 积极参与社区讨论
4. 联系现有维护者申请

---

## 常见问题

### Q: 如何开始我的第一个贡献？
A: 建议从以下方面开始：
1. 修复简单的bug
2. 改进文档
3. 添加测试用例
4. 实现标记为"good first issue"的功能

### Q: 我的PR需要多长时间才能合并？
A: 这取决于：
1. PR的复杂程度
2. 审查者的可用时间
3. 是否需要修改
4. 通常1-7天内会有反馈

### Q: 如何获得帮助？
A: 可以通过以下方式：
1. GitHub Discussions
2. Issue评论区
3. 项目Discord频道
4. 查阅文档

### Q: 我的代码被拒绝了怎么办？
A: 不要灰心！代码审查是为了保证质量：
1. 仔细阅读审查意见
2. 提出问题讨论
3. 按要求修改
4. 重新提交

---

感谢你花时间阅读本贡献指南！我们期待看到你的贡献。🎉

**记住:**
- 保持友善和专业
- 寻求帮助不要犹豫
- 享受编码的过程
- 为开源社区做贡献是件很棒的事！

如有任何问题，请随时联系维护团队。

祝你贡献愉快！ 🚀