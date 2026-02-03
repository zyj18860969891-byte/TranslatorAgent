# 混合架构部署指南

## 概述

本指南说明如何部署基于Node.js + Python的混合架构Translator Agent系统，集成真实的Qwen3模型API。

## 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel前端    │───▶│  Node.js后端    │───▶│ Python处理服务  │
│   (TypeScript)  │    │  (Railway)      │    │  (Qwen3 API)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 组件职责

1. **Vercel前端** - 用户界面，调用Node.js后端API
2. **Node.js后端** - 任务管理、文件处理、API路由
3. **Python处理服务** - 集成Qwen3模型，执行真实AI处理

## 前置要求

- [Node.js](https://nodejs.org/) 16+
- [Python](https://www.python.org/) 3.8+
- [阿里云DashScope](https://dashscope.aliyuncs.com/) API密钥
- [Vercel](https://vercel.com/) 账号
- [Railway](https://railway.app/) 账号

## 部署步骤

### 1. 配置阿里云DashScope

1. 访问 [DashScope控制台](https://dashscope.aliyuncs.com/)
2. 注册/登录账号
3. 获取API密钥
4. 确保账户有足够的配额

### 2. 部署Python处理服务到Railway

#### 方法一：使用Railway CLI（推荐）

```bash
# 安装Railway CLI
npm i -g @railway/cli

# 登录Railway
railway login

# 进入处理服务目录
cd processing_service

# 初始化项目
railway init

# 设置环境变量
railway variables:set DASHSCOPE_API_KEY=your_api_key_here
railway variables:set DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
railway variables:set PRIMARY_MODEL=qwen3-omni-flash-realtime
railway variables:set EMBEDDING_MODEL=qwen3-embedding
railway variables:set SUBTITLE_MODEL=qwen3-vl-rerank

# 部署
railway up
```

#### 方法二：通过Railway控制台

1. 在Railway控制台创建新项目
2. 连接Git仓库，选择 `processing_service` 目录
3. 配置环境变量（同上）
4. 设置启动命令：`python app/main.py`
5. 部署服务

#### 获取Python服务URL

部署成功后，Railway会提供类似：
```
https://translator-agent-processing.up.railway.app
```

### 3. 配置Node.js后端

#### 更新环境变量

在 `backend_api/.env` 文件中添加：

```bash
# Python处理服务URL（替换为你的实际URL）
PYTHON_PROCESSING_SERVICE=https://your-python-service.up.railway.app

# 其他现有配置保持不变
PORT=8000
CORS_ORIGIN=https://your-frontend.vercel.app
...
```

#### 重新部署Node.js后端

```bash
cd backend_api
git add .
git commit -m "Update Python service URL"
git push origin main

# Railway会自动重新部署
```

### 4. 部署前端到Vercel

1. 在Vercel控制台导入项目
2. 选择 `frontend_reconstruction` 目录
3. 配置环境变量：
   ```
   NEXT_PUBLIC_API_URL=https://your-nodejs-backend.up.railway.app
   ```
4. 部署

### 5. 验证部署

#### 检查服务状态

```bash
# 检查Python处理服务
curl https://your-python-service.up.railway.app/health

# 检查Node.js后端
curl https://your-nodejs-backend.up.railway.app/api/health

# 检查前端
访问 https://your-frontend.vercel.app
```

#### 测试完整流程

1. 打开前端应用
2. 创建新任务（视频翻译）
3. 上传视频文件
4. 触发任务处理
5. 验证处理结果

## 配置说明

### Python处理服务配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云API密钥 | 必填 |
| `DASHSCOPE_BASE_URL` | DashScope API地址 | `https://dashscope.aliyuncs.com` |
| `PRIMARY_MODEL` | 主要模型名称 | `qwen3-omni-flash-realtime` |
| `EMBEDDING_MODEL` | 嵌入模型名称 | `qwen3-embedding` |
| `SUBTITLE_MODEL` | 字幕模型名称 | `qwen3-vl-rerank` |
| `MAX_CONCURRENT_REQUESTS` | 最大并发请求数 | `5` |
| `ENABLE_CACHE` | 启用缓存 | `true` |

### Node.js后端配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `PYTHON_PROCESSING_SERVICE` | Python服务URL | `http://localhost:8001` |
| `CORS_ORIGIN` | 允许的CORS来源 | `http://localhost:3000` |
| `PORT` | 服务端口 | `8000` |

## 故障排除

### 常见问题

#### 1. Python服务启动失败

**症状**: Railway部署显示错误，服务无法启动

**解决方案**:
- 检查Python版本是否为3.8+
- 确认requirements.txt中的依赖正确
- 查看Railway日志，检查具体错误信息
- 确保DASHSCOPE_API_KEY已正确设置

#### 2. Qwen3 API调用失败

**症状**: 处理任务时返回错误

**解决方案**:
- 验证DASHSCOPE_API_KEY是否正确
- 检查API配额是否充足
- 确认网络连接正常
- 查看Python服务日志

#### 3. Node.js无法连接Python服务

**症状**: 任务处理超时或连接拒绝

**解决方案**:
- 确认PYTHON_PROCESSING_SERVICE配置正确
- 检查两个服务是否都在运行
- 验证Railway内部网络连接
- 检查服务URL是否正确（注意https/http）

#### 4. CORS错误

**症状**: 浏览器控制台显示CORS错误

**解决方案**:
- 在Node.js后端CORS配置中添加前端域名
- 确保Vercel域名匹配通配符模式
- 检查CORS中间件配置

#### 5. 文件上传失败

**症状**: 上传文件时出现错误

**解决方案**:
- 检查文件大小限制
- 确认上传目录权限
- 验证multer配置
- 检查磁盘空间

### 日志查看

#### Railway日志
```bash
# 查看Python服务日志
railway logs

# 查看Node.js后端日志
# 在Railway控制台中查看
```

#### 本地调试
```bash
# Python服务
cd processing_service
python -m app.main

# Node.js后端
cd backend_api
npm run dev
```

## 性能优化

### 1. 缓存策略
- Python服务已启用内存缓存
- 可配置Redis缓存提升性能
- 调整`CACHE_TTL`控制缓存时间

### 2. 并发处理
- 调整`MAX_CONCURRENT_REQUESTS`控制并发数
- 根据API配额合理设置
- 避免超出DashScope限制

### 3. 数据库优化
- 当前使用内存存储，适合小规模
- 生产环境建议使用Redis或MongoDB
- 实现持久化存储

## 监控和告警

### 关键指标
- 服务响应时间
- API调用成功率
- 任务处理成功率
- 资源使用率

### 建议配置
- Railway监控告警
- 日志聚合服务
- 性能监控面板

## 成本控制

### DashScope成本
- 监控API调用次数
- 设置使用限额
- 选择合适的模型（qwen3-omni-flash-realtime成本较低）

### Railway成本
- 使用免费额度
- 设置使用限制
- 优化资源使用

## 安全建议

1. **API密钥保护**
   - 不要硬编码在代码中
   - 使用环境变量
   - 定期轮换密钥

2. **访问控制**
   - 实施API密钥验证
   - 限制访问频率
   - 监控异常访问

3. **数据安全**
   - 加密敏感数据
   - 安全删除临时文件
   - 实施数据备份

## 更新维护

### 更新Qwen3模型
1. 修改`processing_service/config/settings.py`中的模型配置
2. 重新部署Python服务
3. 验证新模型功能

### 更新依赖
```bash
cd processing_service
pip install -r requirements.txt --upgrade
```

### 回滚部署
- 使用Railway的版本回滚功能
- 保留旧版本配置
- 测试后再切换

## 支持

如有问题，请：
1. 查看日志信息
2. 检查配置文档
3. 提交Issue到GitHub
4. 联系开发团队

## 附录

### A. 环境变量清单

#### Python处理服务
```bash
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
PRIMARY_MODEL=qwen3-omni-flash-realtime
EMBEDDING_MODEL=qwen3-embedding
SUBTITLE_MODEL=qwen3-vl-rerank
MAX_CONCURRENT_REQUESTS=5
ENABLE_CACHE=true
```

#### Node.js后端
```bash
PYTHON_PROCESSING_SERVICE=https://your-service.up.railway.app
CORS_ORIGIN=https://your-frontend.vercel.app
PORT=8000
```

### B. API端点清单

#### Python处理服务
- `GET /health` - 健康检查
- `POST /api/v1/process/tasks/{task_id}` - 处理任务
- `POST /api/v1/process/video` - 处理视频
- `POST /api/v1/process/subtitle` - 处理字幕
- `POST /api/v1/process/translate` - 翻译文本

#### Node.js后端（保持不变）
- `GET /api/health` - 健康检查
- `POST /api/v1/tasks` - 创建任务
- `GET /api/v1/tasks/:taskId` - 获取任务状态
- `POST /api/v1/tasks/:taskId/process` - 处理任务
- `POST /api/v1/translation/translate` - 翻译
- `POST /api/v1/video/process` - 视频处理
- `POST /api/v1/subtitle/process` - 字幕处理

---

**部署完成后，系统将使用真实的Qwen3模型处理任务，提供高质量的AI处理能力！**