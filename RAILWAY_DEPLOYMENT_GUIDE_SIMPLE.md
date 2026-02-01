# OpenManus TranslatorAgent Railway 部署指南

## 📋 概述

本指南详细说明了如何将 OpenManus TranslatorAgent 项目部署到 Railway 平台。Railway 是一个现代化的云部署平台，支持 Node.js、Python、Docker 等多种技术栈。

## 🚀 快速开始

### 1. 准备工作

确保您已具备以下条件：
- Railway 账户（免费账户即可）
- Git 仓库（推荐使用 GitHub）
- 项目代码已推送到远程仓库

### 2. 使用自动化脚本部署

```bash
# 克隆项目
git clone <your-repo-url>
cd TranslatorAgent

# 运行部署脚本
chmod +x deploy_railway.sh
./deploy_railway.sh
```

自动化脚本将完成以下工作：
- 检查必要工具
- 安装 Railway CLI
- 初始化 Railway 项目
- 创建配置文件
- 部署到 Railway

## 📁 项目结构

```
TranslatorAgent/
├── railway.toml              # Railway 配置文件
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
├── scripts/
│   ├── setup.sh            # 环境设置脚本
│   ├── start.sh            # 启动脚本
│   ├── bundle-artifact.sh   # 打包脚本
│   └── cleanup.sh          # 清理脚本
├── backend/                 # 后端代码
├── frontend/                # 前端代码
├── data/                    # 数据存储目录
├── tasks/                   # 任务存储目录
└── terminology/            # 术语库目录
```

## 🔧 详细配置

### 1. Railway 配置 (railway.toml)

```toml
[build]
command = "bash scripts/setup.sh"

[deploy]
startCommand = "bash scripts/start.sh"

[env]
NODE_ENV = "production"
PORT = "3000"

[[mount]]
source = "data"
destination = "/data"

[[mount]]
source = "tasks"
destination = "/tasks"
```

### 2. 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# 百炼 API 配置
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com

# OpenRouter API 配置 (用于 mimo-v2-flash)
OPENROUTER_API_KEY=your_openrouter_api_key

# ModelScope API 配置
MODELSCOPE_API_KEY=your_modelscope_api_key
MODELSCOPE_BASE_URL=https://api.modelscope.cn/api/v1

# 前端配置
VITE_API_BASE_URL=https://your-railway-app.railway.app
VITE_ENABLE_API_INTEGRATION=true

# 应用配置
NODE_ENV=production
PORT=3000
```

### 3. Volume 配置

在 Railway 控制台配置两个 Volume：

1. **data Volume**
   - 名称: `data`
   - 挂载点: `/data`
   - 用途: 存储翻译数据、术语库等

2. **tasks Volume**
   - 名称: `tasks`
   - 挂载点: `/tasks`
   - 用途: 存储任务状态和历史记录

## 📦 依赖管理

### Python 依赖

```txt
# 核心依赖
openai>=1.0.0
dashscope>=1.15.0
pydantic>=2.0.0
ffmpeg-python>=0.2.0

# Web 框架
fastapi>=0.100.0
uvicorn>=0.20.0
cors>=2.8.5

# 数据处理
pandas>=1.5.0
numpy>=1.24.0
opencv-python>=4.8.0

# 工具库
requests>=2.31.0
python-multipart>=0.0.6
aiofiles>=23.0.0
```

### Node.js 依赖

```bash
cd frontend
npm install
npm run build
```

## 🚀 部署步骤

### 方法一：使用 Railway CLI

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录 Railway
railway login

# 3. 初始化项目
railway init

# 4. 部署项目
railway up
```

### 方法二：使用 GitHub 集成

1. 将项目推送到 GitHub
2. 在 Railway 控制台连接 GitHub 仓库
3. Railway 会自动检测项目类型并部署

### 方法三：使用 Docker

如果需要自定义 Docker 镜像：

```dockerfile
FROM node:18-alpine

# 安装 Python
RUN apk add --no-cache python3 py3-pip

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制 package.json
COPY frontend/package.json frontend/
RUN cd frontend && npm install

# 复制源代码
COPY . .

# 构建前端
RUN cd frontend && npm run build

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["bash", "scripts/start.sh"]
```

## 🔧 启动脚本

### setup.sh - 环境设置

```bash
#!/bin/bash
echo "🔧 设置 OpenManus TranslatorAgent 环境..."

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd frontend
npm install
cd ..

# 创建必要目录
mkdir -p data tasks terminology

# 设置权限
chmod +x scripts/*.sh

echo "✅ 环境设置完成!"
```

### start.sh - 服务启动

```bash
#!/bin/bash
echo "🚀 启动 OpenManus TranslatorAgent..."

# 打包前端界面
bash scripts/bundle-artifact.sh

# 启动后端服务
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT --reload &

# 启动前端服务
cd ../frontend
npm run build
npm run preview -- --host 0.0.0.0 --port $PORT

echo "✅ 服务启动完成!"
```

### bundle-artifact.sh - 前端打包

```bash
#!/bin/bash
echo "📦 打包前端界面..."

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

echo "✅ 前端界面打包完成!"
```

### cleanup.sh - 清理脚本

```bash
#!/bin/bash
echo "🧹 清理临时文件..."

# 清理任务临时文件
find tasks/ -name "*.tmp" -delete 2>/dev/null || true
find tasks/ -name "*.temp" -delete 2>/dev/null || true

# 清理数据临时文件
find data/ -name "*.tmp" -delete 2>/dev/null || true
find data/ -name "*.temp" -delete 2>/dev/null || true

# 清理日志文件
find . -name "*.log" -delete 2>/dev/null || true

echo "✅ 清理完成!"
```

## 📊 监控与日志

### 查看日志

```bash
# 实时查看日志
railway logs --tail 10

# 查看特定服务的日志
railway logs --service backend

# 下载日志
railway logs --download
```

### 监控指标

Railway 提供以下监控指标：
- CPU 使用率
- 内存使用率
- 网络流量
- 响应时间
- 错误率

### 性能优化

1. **资源限制**
   ```toml
   [deploy]
   cpu = 0.5
   memory = 512
   ```

2. **自动扩缩容**
   ```toml
   [deploy]
   minInstances = 1
   maxInstances = 3
   ```

## 🔒 安全配置

### 1. API 密钥管理

- 使用 Railway 的环境变量管理功能
- 定期轮换 API 密钥
- 设置访问权限

### 2. 网络安全

- 配置 HTTPS
- 设置 CORS 策略
- 限制访问频率

### 3. 数据安全

- 加密敏感数据
- 定期备份数据
- 设置访问控制

## 🚨 故障排除

### 常见问题

1. **部署失败**
   - 检查依赖版本兼容性
   - 确认环境变量配置
   - 查看详细错误日志

2. **服务无法访问**
   - 检查端口配置
   - 确认防火墙设置
   - 验证域名解析

3. **性能问题**
   - 优化代码性能
   - 调整资源配置
   - 启用缓存机制

### 调试技巧

```bash
# 本地测试
railway run

# 检查环境变量
railway env

# 重启服务
railway restart

# 回滚部署
railway rollback
```

## 📈 生产环境优化

### 1. 性能优化

- 使用 CDN 加速静态资源
- 启用 Gzip 压缩
- 配置缓存策略

### 2. 成本优化

- 使用免费套餐
- 优化资源配置
- 启用自动休眠

### 3. 可用性优化

- 配置多区域部署
- 设置健康检查
- 启用自动备份

## 🔄 更新与维护

### 更新部署

```bash
# 推送代码到 GitHub
git push origin main

# Railway 会自动重新部署
# 或者手动触发部署
railway up
```

### 备份数据

```bash
# 备份数据 Volume
railway volume:backup data

# 备份数据库
railway db:backup
```

### 回滚版本

```bash
# 查看部署历史
railway deployments

# 回滚到特定版本
railway rollback <deployment-id>
```

## 📞 技术支持

### 官方文档
- [Railway 文档](https://docs.railway.app/)
- [Railway CLI 参考](https://docs.railway.app/reference/cli)

### 社区支持
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub](https://github.com/railwayapp)

### 项目支持
- [OpenManus TranslatorAgent GitHub](https://github.com/your-repo)
- [项目文档](https://docs.your-project.com)

---

## 🎉 总结

通过本指南，您可以轻松地将 OpenManus TranslatorAgent 部署到 Railway 平台。Railway 提供了简单易用的部署流程，同时支持自动扩缩容、监控和日志管理等功能。

部署完成后，您将获得：
- 🌐 全球可访问的 Web 应用
- 📊 实时监控和日志
- 🔒 安全的环境配置
- 💰 经济实惠的定价方案

开始您的 Railway 部署之旅吧！