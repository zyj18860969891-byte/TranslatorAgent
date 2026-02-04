# Python处理服务部署指南

## 概述

本指南将帮助您将Python处理服务部署到Railway，以解决ECONNREFUSED错误并实现完整的AI处理功能。

## 问题分析

根据Railway部署日志，当前问题：
- Python处理服务未部署到Railway
- 后端尝试调用Python服务时出现ECONNREFUSED错误
- 需要在Railway上部署独立的Python处理服务

## 部署步骤

### 1. 准备工作

确保您已安装：
- Railway CLI
- Node.js和npm
- Python 3.8+

### 2. 部署Python处理服务

#### 方法一：使用Railway CLI（推荐）

```bash
# 1. 安装Railway CLI
npm install -g @railway/cli

# 2. 登录Railway
railway login

# 3. 进入Python处理服务目录
cd processing_service

# 4. 初始化Railway项目
railway init

# 5. 部署服务
railway up
```

#### 方法二：使用Windows批处理脚本

```bash
# 运行Windows部署脚本
deploy_processing_service.bat
```

### 3. 配置环境变量

部署完成后，在Railway控制台中设置以下环境变量：

```bash
# 在Railway项目设置中添加：
DASHSCOPE_API_KEY=your_actual_dashscope_api_key
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
PYTHONUNBUFFERED=1
```

### 4. 更新后端配置

获取Python处理服务的URL后，更新backend_api/railway.toml：

```toml
[env]
# 环境变量配置
PORT = "8000"
NODE_ENV = "production"
PYTHON_PROCESSING_SERVICE = "https://your-processing-service.railway.app"
```

### 5. 重新部署后端服务

```bash
# 进入后端目录
cd backend_api

# 重新部署
railway up
```

## 验证部署

### 1. 检查Python服务状态

```bash
# 检查Railway服务状态
railway service list

# 检查服务日志
railway logs
```

### 2. 测试API端点

```bash
# 测试Python服务健康检查
curl https://your-processing-service.railway.app/health

# 测试任务处理
curl -X POST https://your-processing-service.railway.app/process \
  -H "Content-Type: application/json" \
  -d '{"task_id": "test", "data": {"text": "Hello World"}}'
```

### 3. 集成测试

运行完整的集成测试：
```bash
cd backend_api
npm test
```

## 故障排除

### 常见问题

1. **ECONNREFUSED错误**
   - 确保Python服务已正确部署
   - 检查服务URL是否正确
   - 验证网络连接

2. **CORS错误**
   - 确保ALLOWED_ORIGINS包含正确的Vercel域名
   - 检查CORS中间件配置

3. **API密钥错误**
   - 确保DASHSCOPE_API_KEY正确设置
   - 检查API密钥权限

### 调试步骤

1. 检查Railway部署日志：
   ```bash
   railway logs
   ```

2. 检查Python服务日志：
   ```bash
   railway logs --service processing
   ```

3. 本地测试Python服务：
   ```bash
   cd processing_service
   python -m uvicorn app.main:app --reload
   ```

## 完成检查清单

- [ ] Python处理服务已部署到Railway
- [ ] 环境变量已正确设置
- [ ] 后端服务已更新并重新部署
- [ ] 所有API端点正常工作
- [ ] 完整的集成测试通过

## 后续优化

1. **性能优化**
   - 添加缓存机制
   - 优化并发处理
   - 实现负载均衡

2. **监控和日志**
   - 添加性能监控
   - 实现错误追踪
   - 设置告警机制

3. **安全增强**
   - API密钥轮换
   - 访问控制
   - 数据加密

## 联系支持

如果遇到问题，请检查：
1. Railway控制台状态
2. 部署日志
3. 环境变量配置
4. 网络连接状态

---

**注意：** 部署完成后，请确保更新所有相关的文档和配置文件。