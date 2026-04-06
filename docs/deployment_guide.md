# AI宠物MVP - 部署指南

本文档提供了AI宠物MVP项目的完整部署指南，涵盖各种环境和场景。

## 目录
- [快速部署](#快速部署)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker容器化](#docker容器化)
- [Windows系统部署](#windows系统部署)
- [Linux系统部署](#linux系统部署)
- [macOS系统部署](#macos系统部署)
- [云端部署](#云端部署)
- [性能优化](#性能优化)
- [监控维护](#监控维护)
- [故障排除](#故障排除)
- [安全指南](#安全指南)

## 快速部署

### 5分钟快速启动
如果你只是想快速体验AI宠物MVP，可以使用以下最简单的方式：
bash

1. 克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

2. 运行一键安装脚本（Linux/macOS）
chmod +x scripts/quick_start.sh

./scripts/quick_start.sh

Windows用户
scripts\quick_start.bat

复制
### 最小化配置
创建最小配置文件 `config/minimal_config.json`:
json

{

"ai": {

"type": "ollama",

"model": "qwen:7b"

},

"ui": {

"theme": "light"

}

}

复制
运行：
bash

python run_app.py --config config/minimal_config.json

复制
## 开发环境部署

### 完整开发环境设置

#### 1. 系统准备
bash

Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

sudo apt install python3.9 python3.9-venv python3.9-dev git -y

macOS
brew install python@3.9 git

Windows
1. 安装Python 3.9+ from python.org
2. 安装Git from git-scm.com
复制
#### 2. 项目设置
bash

克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

创建虚拟环境
python -m venv venv

激活虚拟环境
Linux/macOS
source venv/bin/activate

Windows
venv\Scripts\activate

复制
#### 3. 安装依赖
bash

安装基础依赖
pip install -r requirements.txt

安装开发依赖
pip install -r requirements-dev.txt

安装Ollama（如果需要本地AI）
Linux/macOS
curl -fsSL https://ollama.com/install.sh| sh

Windows: 从官网下载安装程序
下载AI模型
ollama pull qwen:7b

复制
#### 4. 初始化项目
bash

创建必要目录
mkdir -p data/config data/memory logs backups

生成默认配置
python scripts/init_config.py

初始化数据库
python scripts/init_db.py

复制
#### 5. 运行开发服务器
bash

方式1: 直接运行
python run_app.py

方式2: 使用开发服务器（支持热重载）
python scripts/dev_server.py

方式3: 调试模式
python run_app.py --debug

复制
### 开发工具配置

#### VS Code配置
创建 `.vscode/settings.json`:
json

{

"python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",

"python.linting.enabled": true,

"python.linting.flake8Enabled": true,

"python.formatting.provider": "black",

"python.formatting.blackArgs": [

"--line-length=88"

],

"editor.formatOnSave": true,

"editor.codeActionsOnSave": {

"source.organizeImports": true

},

"files.exclude": {

"**/pycache": true,

"**/.pytest_cache": true

}

}

复制
#### PyCharm配置
1. 设置Python解释器为虚拟环境
2. 启用PEP 8检查
3. 配置测试运行器为pytest
4. 设置代码风格为Black

## 生产环境部署

### 单机部署方案

#### 1. 服务器准备
bash

以Ubuntu 22.04为例
更新系统
sudo apt update && sudo apt upgrade -y

安装基础软件
sudo apt install python3.9 python3.9-venv python3.9-dev nginx supervisor -y

安装PostgreSQL（可选）
sudo apt install postgresql postgresql-contrib -y

复制
#### 2. 应用部署
bash

创建应用用户
sudo useradd -m -s /bin/bash ai-pet

sudo passwd ai-pet

切换到应用用户
sudo su - ai-pet

克隆代码
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

创建虚拟环境
python3.9 -m venv venv

source venv/bin/activate

安装依赖
pip install -r requirements.txt

pip install gunicorn

复制
#### 3. 环境配置
创建 `.env.production`:
env

应用设置
AI_PET_ENV=production

AI_PET_DEBUG=false

AI_PET_SECRET_KEY=your-secret-key-here

数据库设置
DATABASE_URL=sqlite:///data/ai_pet.db

或使用PostgreSQL
DATABASE_URL=postgresql://username:password@localhost/ai_pet
AI设置
AI_SERVICE=ollama

AI_MODEL=qwen:7b

AI_TIMEOUT=60

日志设置
LOG_LEVEL=INFO

LOG_FILE=/var/log/ai-pet/app.log

复制
#### 4. 创建服务文件
创建 `/etc/systemd/system/ai-pet.service`:
ini

[Unit]

Description=AI Pet MVP Application

After=network.target

[Service]

User=ai-pet

Group=ai-pet

WorkingDirectory=/home/ai-pet/ai-pet-mvp

Environment="PATH=/home/ai-pet/ai-pet-mvp/venv/bin"

EnvironmentFile=/home/ai-pet/ai-pet-mvp/.env.production

ExecStart=/home/ai-pet/ai-pet-mvp/venv/bin/gunicorn \

--workers 3 \

--worker-class sync \

--bind 0.0.0.0:8000 \

--timeout 120 \

"run_app:create_app()"

Restart=always

RestartSec=10

[Install]

WantedBy=multi-user.target

复制
#### 5. 配置Nginx
创建 `/etc/nginx/sites-available/ai-pet`:
nginx

server {

listen 80;

server_name your-domain.com;

复制
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /static/ {
    alias /home/ai-pet/ai-pet-mvp/static/;
    expires 30d;
}

location /media/ {
    alias /home/ai-pet/ai-pet-mvp/media/;
    expires 30d;
}
}

复制
启用配置：
bash

sudo ln -s /etc/nginx/sites-available/ai-pet /etc/nginx/sites-enabled/

sudo nginx -t

sudo systemctl reload nginx

复制
#### 6. 启动服务
bash

启动应用服务
sudo systemctl daemon-reload

sudo systemctl start ai-pet

sudo systemctl enable ai-pet

查看状态
sudo systemctl status ai-pet

复制
### 高可用部署方案

#### 负载均衡配置
使用Nginx作为负载均衡器：
nginx

upstream ai_pet_servers {

least_conn;

server 192.168.1.101:8000;

server 192.168.1.102:8000;

server 192.168.1.103:8000;

keepalive 32;

}

server {

listen 80;

复制
location / {
    proxy_pass http://ai_pet_servers;
    # ... 其他代理设置
}
}

复制
#### 数据库集群
使用PostgreSQL主从复制：
1. 配置主数据库
2. 设置从数据库
3. 配置流复制
4. 设置故障转移

#### 文件存储
使用对象存储或网络共享：
- AWS S3 / 阿里云OSS
- NFS共享
- GlusterFS集群

## Docker容器化

### Docker基础部署

#### 1. Dockerfile
创建 `Dockerfile`:
dockerfile

使用Python 3.9作为基础镜像
FROM python:3.9-slim

设置工作目录
WORKDIR /app

安装系统依赖
RUN apt-get update && apt-get install -y \

gcc \

g++ \

&& rm -rf /var/lib/apt/lists/*

复制依赖文件
COPY requirements.txt .

安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

复制应用代码
COPY . .

创建非root用户
RUN useradd -m -u 1000 ai-pet && chown -R ai-pet:ai-pet /app

USER ai-pet

创建必要目录
RUN mkdir -p data/config data/memory logs backups

暴露端口
EXPOSE 8000

运行应用
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "run_app:create_app()"]

复制
#### 2. Docker Compose配置
创建 `docker-compose.yml`:
yaml

version: '3.8'

services:

ai-pet:

build: .

ports:

"8000:8000"

volumes:

./data:/app/data

./logs:/app/logs

./backups:/app/backups

environment:

AI_PET_ENV=production

DATABASE_URL=sqlite:///data/ai_pet.db

restart: unless-stopped

networks:

ai-pet-network

ollama:

image: ollama/ollama:latest

ports:

"11434:11434"

volumes:

ollama_data:/root/.ollama

restart: unless-stopped

networks:

ai-pet-network

nginx:

image: nginx:alpine

ports:

"80:80"

volumes:

./nginx.conf:/etc/nginx/nginx.conf

./ssl:/etc/nginx/ssl

depends_on:

ai-pet

restart: unless-stopped

networks:

ai-pet-network

volumes:

ollama_data:

networks:

ai-pet-network:

driver: bridge

复制
#### 3. 构建和运行
bash

构建镜像
docker-compose build

启动服务
docker-compose up -d

查看日志
docker-compose logs -f

停止服务
docker-compose down

复制
### Kubernetes部署

#### 1. 创建命名空间
yaml

namespace.yaml
apiVersion: v1

kind: Namespace

metadata:

name: ai-pet

复制
#### 2. 创建配置
yaml

configmap.yaml
apiVersion: v1

kind: ConfigMap

metadata:

name: ai-pet-config

namespace: ai-pet

data:

AI_PET_ENV: "production"

LOG_LEVEL: "INFO"

复制
#### 3. 创建部署
yaml

deployment.yaml
apiVersion: apps/v1

kind: Deployment

metadata:

name: ai-pet

namespace: ai-pet

spec:

replicas: 3

selector:

matchLabels:

app: ai-pet

template:

metadata:

labels:

app: ai-pet

spec:

containers:

name: ai-pet

image: your-registry/ai-pet:latest

ports:

containerPort: 8000

envFrom:

configMapRef:

name: ai-pet-config

volumeMounts:

name: data

mountPath: /app/data

name: logs

mountPath: /app/logs

volumes:

name: data

persistentVolumeClaim:

claimName: ai-pet-data

name: logs

emptyDir: {}

复制
#### 4. 创建服务
yaml

service.yaml
apiVersion: v1

kind: Service

metadata:

name: ai-pet-service

namespace: ai-pet

spec:

selector:

app: ai-pet

ports:

protocol: TCP

port: 80

targetPort: 8000

type: LoadBalancer

复制
## Windows系统部署

### 桌面应用部署

#### 1. 安装Python
1. 访问 [python.org](https://www.python.org/downloads/)
2. 下载Python 3.9+安装程序
3. 安装时勾选"Add Python to PATH"

#### 2. 使用安装程序
我们提供了Windows安装程序：
1. 下载 `AI-Pet-MVP-Setup.exe`
2. 运行安装程序
3. 按照向导完成安装
4. 桌面会创建快捷方式

#### 3. 手动安装
powershell

打开PowerShell
克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

创建虚拟环境
python -m venv venv

venv\Scripts\activate

安装依赖
pip install -r requirements.txt

运行应用
python run_app.py

复制
#### 4. 创建Windows服务
创建服务脚本 `install_windows_service.py`:
python

import win32serviceutil

import win32service

import win32event

import servicemanager

import sys

import os

class AIPetService(win32serviceutil.ServiceFramework):

svc_name= "AIPetService"

svc_display_name= "AI宠物MVP服务"

svc_description= "AI宠物MVP应用程序后台服务"

复制
def __init__(self, args):
    win32serviceutil.ServiceFramework.__init__(self, args)
    self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
def SvcStop(self):
    self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
    win32event.SetEvent(self.hWaitStop)
    
def SvcDoCommand(self):
    servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                        servicemanager.PYS_SERVICE_STARTED,
                        (self._svc_name_, ''))
    # 运行应用
    os.system("python run_app.py")
if name== 'main':

if len(sys.argv) == 1:

servicemanager.Initialize()

servicemanager.PrepareToHostSingle(AIPetService)

servicemanager.StartServiceCtrlDispatcher()

else:

win32serviceutil.HandleCommandLine(AIPetService)

复制
安装服务：
powershell

python install_windows_service.py install

net start AIPetService

复制
## Linux系统部署

### 桌面环境
bash

Ubuntu/Debian
sudo apt update

sudo apt install python3.9 python3.9-venv git

克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

运行
python3 run_app.py

复制
### 创建桌面快捷方式
创建 `~/.local/share/applications/ai-pet.desktop`:
ini

[Desktop Entry]

Version=1.0

Type=Application

Name=AI宠物MVP

Comment=AI宠物桌面应用

Exec=/home/user/ai-pet-mvp/venv/bin/python /home/user/ai-pet-mvp/run_app.py

Icon=/home/user/ai-pet-mvp/assets/icon.png

Terminal=false

Categories=Utility;

复制
## macOS系统部署

### 桌面应用
bash

安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

安装Python
brew install python@3.9

克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

创建虚拟环境
python3 -m venv venv

source venv/bin/activate

安装依赖
pip install -r requirements.txt

运行
python run_app.py

复制
### 创建应用程序包
使用PyInstaller创建macOS应用：
bash

安装PyInstaller
pip install pyinstaller

创建应用
pyinstaller --onefile --windowed --name="AI宠物" run_app.py

应用程序会在dist目录中
复制
## 云端部署

### 部署到云服务器

#### AWS EC2部署
bash

连接到EC2实例
ssh -i your-key.pem ubuntu@your-ec2-ip

安装Docker
sudo apt update

sudo apt install docker.io docker-compose -y

克隆项目
git clone https://github.com/LaugBo/ai-pet-mvp.git

cd ai-pet-mvp

使用Docker运行
docker-compose up -d

复制
#### 使用云数据库
配置使用云数据库（如AWS RDS）：
python

数据库配置
DATABASE_URL = "postgresql://username:password@your-rds-endpoint:5432/ai_pet"

复制
### 无服务器部署
使用AWS Lambda + API Gateway：

创建 `lambda_function.py`:
python

import json

from src.core.ai.adapter import AIManager

def lambda_handler(event, context):

# 处理请求

user_message = event.get('message', '')

复制
# 创建AI管理器
ai_manager = AIManager({
    "adapter_type": "openai",
    "api_key": os.getenv("OPENAI_API_KEY")
})

# 获取响应
response = ai_manager.generate_response(user_message)

return {
    'statusCode': 200,
    'body': json.dumps({'response': response})
}
复制
## 性能优化

### 应用性能优化

#### 1. 数据库优化
python

使用连接池
SQLALCHEMY_POOL_SIZE = 20

SQLALCHEMY_MAX_OVERFLOW = 100

SQLALCHEMY_POOL_RECYCLE = 3600

启用查询缓存
SQLALCHEMY_ENGINE_OPTIONS = {

"pool_pre_ping": True,

"pool_recycle": 3600,

}

复制
#### 2. 缓存配置
python

使用Redis缓存
CACHE_TYPE = "redis"

CACHE_REDIS_URL = "redis://localhost:6379/0"

CACHE_DEFAULT_TIMEOUT = 300

复制
#### 3. 静态文件优化
nginx

Nginx配置
location /static/ {

alias /path/to/static/;

expires 365d;

add_header Cache-Control "public, immutable";

}

复制
### 监控配置

#### 1. 日志监控
python

结构化日志
import structlog

structlog.configure(

processors=[

structlog.stdlib.filter_by_level,

structlog.stdlib.add_logger_name,

structlog.stdlib.add_log_level,

structlog.stdlib.PositionalArgumentsFormatter(),

structlog.processors.TimeStamper(fmt="iso"),

structlog.processors.StackInfoRenderer(),

structlog.processors.format_exc_info,

structlog.processors.JSONRenderer()

],

context_class=dict,

logger_factory=structlog.stdlib.LoggerFactory(),

wrapper_class=structlog.stdlib.BoundLogger,

cache_logger_on_first_use=True,

)

复制
#### 2. 性能监控
使用Prometheus + Grafana：
- 监控API响应时间
- 监控错误率
- 监控资源使用率
- 设置警报规则

## 监控维护

### 日常监控

#### 1. 健康检查
创建健康检查端点：
python

@app.route('/health')

def health_check():

return {

'status': 'healthy',

'timestamp': datetime.now().isoformat(),

'version': '1.0.0'

}

复制
#### 2. 监控指标
bash

查看应用状态
curl http://localhost:8000/health

查看系统资源
top

htop

查看日志
tail -f logs/app.log

复制
### 备份策略

#### 1. 自动备份
创建备份脚本 `scripts/auto_backup.py`:
python

import schedule

import time

from scripts.backup import BackupManager

def daily_backup():

manager = BackupManager()

manager.create_backup()

每天凌晨2点备份
schedule.every().day.at("02:00").do(daily_backup)

while True:

schedule.run_pending()

time.sleep(60)

复制
#### 2. 备份到云存储
python

import boto3

from scripts.backup import BackupManager

def backup_to_s3():

manager = BackupManager()

backup_path = manager.create_backup()

复制
# 上传到S3
s3 = boto3.client('s3')
s3.upload_file(
    str(backup_path),
    'your-bucket-name',
    f'backups/{backup_path.name}'
)
复制
## 故障排除

### 常见问题解决

#### 1. 应用无法启动
bash

检查Python版本
python --version

检查依赖
pip list

检查端口占用
netstat -tulpn | grep :8000

查看日志
tail -f logs/error.log

复制
#### 2. AI服务连接失败
bash

检查Ollama服务
curl http://localhost:11434/api/tags

检查网络连接
ping your-ai-server

检查防火墙
sudo ufw status

复制
#### 3. 数据库问题
bash

检查数据库连接
python scripts/check_db.py

修复SQLite数据库
sqlite3 data/ai_pet.db ".recover" | sqlite3 data/ai_pet_fixed.db

复制
### 调试模式
bash

启用调试
export AI_PET_DEBUG=true

python run_app.py --debug

详细日志
export LOG_LEVEL=DEBUG

复制
## 安全指南

### 安全最佳实践

#### 1. 环境安全
bash

使用强密码
export DATABASE_PASSWORD=$(openssl rand -base64 32)

定期轮换密钥
export SECRET_KEY=$(openssl rand -hex 32)

使用HTTPS
配置SSL证书
复制
#### 2. 访问控制
nginx

限制访问IP
location /admin/ {

allow 192.168.1.0/24;

deny all;

}

速率限制
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

复制
#### 3. 数据安全
- 加密敏感数据
- 定期备份
- 访问日志审计
- 输入验证和过滤

### 安全扫描
bash

使用安全工具扫描
Bandit - Python安全扫描
bandit -r src/

Safety - 依赖安全检查
safety check

Trivy - 容器安全扫描
trivy image your-image:latest

复制
---

## 附录

### 部署检查清单
- [ ] 系统要求满足
- [ ] 依赖安装完成
- [ ] 配置文件正确
- [ ] 数据库初始化
- [ ] 服务启动成功
- [ ] 网络访问正常
- [ ] 监控配置完成
- [ ] 备份策略就绪
- [ ] 安全配置完成

### 性能基准
- 启动时间: < 5秒
- API响应: < 200ms
- 并发用户: 100+
- 内存使用: < 512MB
- CPU使用: < 30%

### 支持联系方式
- 文档: [docs.example.com](https://docs.example.com)
- 问题: [GitHub Issues](https://github.com/LaugBo/ai-pet-mvp/issues)
- 邮件: support@example.com
- Discord: [加入社区](https://discord.gg/your-invite)
