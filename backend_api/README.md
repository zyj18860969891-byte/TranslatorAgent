# Translator Agent 后端 API 服务

## 项目概述

Translator Agent 后端 API 服务是一个基于 Node.js + Express 构建的 RESTful API 服务，为 Translator Agent 前端提供完整的任务管理、文件处理、进度跟踪和记忆层操作功能。

## 核心功能

### 1. 任务管理
- ✅ 创建任务
- ✅ 查询任务状态
- ✅ 更新任务状态
- ✅ 更新任务进度
- ✅ 获取任务列表
- ✅ 清理旧任务
- ✅ 任务统计

### 2. 文件处理
- ✅ 单文件上传
- ✅ 批量文件上传
- ✅ 文件类型验证
- ✅ 文件大小限制

### 3. 记忆层操作
- ✅ 添加对话历史
- ✅ 添加处理结果
- ✅ 添加中间数据

### 4. 实时处理模拟
- ✅ 任务处理进度模拟
- ✅ 实时状态更新
- ✅ 错误处理

### 5. 系统监控
- ✅ 健康检查
- ✅ 系统信息
- ✅ 性能指标

## API 端点

### 健康检查
```
GET /api/health
```

### 任务管理
```
POST   /api/v1/tasks                    - 创建任务
GET    /api/v1/tasks/:taskId            - 获取任务状态
POST   /api/v1/tasks/:taskId/status     - 更新任务状态
POST   /api/v1/tasks/:taskId/progress   - 更新进度
POST   /api/v1/tasks/:taskId/files      - 添加文件
POST   /api/v1/tasks/:taskId/memory     - 添加到记忆层
GET    /api/v1/tasks                    - 获取任务列表
POST   /api/v1/tasks/cleanup            - 清理旧任务
GET    /api/v1/tasks/stats              - 获取任务统计
POST   /api/v1/tasks/:taskId/process    - 模拟任务处理
```

### 文件上传
```
POST   /api/v1/upload                   - 上传文件
POST   /api/v1/upload/batch             - 批量上传文件
```

### 系统信息
```
GET    /api/v1/system/info              - 系统信息
```

## 数据格式

### 任务创建请求
```json
{
  "module": "translation",
  "taskName": "视频翻译任务",
  "files": [
    {
      "name": "video.mp4",
      "type": "video/mp4",
      "url": "http://example.com/video.mp4"
    }
  ],
  "instructions": "将视频中的英文翻译成中文",
  "options": {
    "targetLanguage": "zh-CN",
    "quality": "high"
  }
}
```

### 任务状态响应
```json
{
  "taskId": "uuid-string",
  "status": "created|queued|processing|completed|failed",
  "progress": 50,
  "message": "正在处理任务...",
  "files": {
    "uploaded": ["video.mp4"],
    "processed": ["video_translated.mp4"],
    "failed": []
  },
  "memoryLayer": {
    "conversationHistory": [],
    "processingResults": [],
    "intermediateData": []
  },
  "createdAt": "2026-01-21T10:00:00.000Z",
  "updatedAt": "2026-01-21T10:00:30.000Z",
  "completedAt": null,
  "error": null
}
```

### API 响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": {...},
  "timestamp": "2026-01-21T10:00:00.000Z"
}
```

### 错误响应格式
```json
{
  "error": "错误信息",
  "code": 400,
  "details": "详细错误信息",
  "timestamp": "2026-01-21T10:00:00.000Z"
}
```

## 安装和运行

### 1. 安装依赖
```bash
cd backend_api
npm install
```

### 2. 配置环境变量
```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，根据需要修改配置
```

### 3. 启动服务
```bash
# 开发模式（使用 nodemon，自动重启）
npm run dev

# 生产模式
npm start
```

### 4. 验证服务
```bash
# 检查健康状态
curl http://localhost:8000/api/health

# 预期响应
{
  "success": true,
  "message": "成功",
  "data": {
    "status": "healthy",
    "timestamp": "2026-01-21T10:00:00.000Z",
    "uptime": 123.456,
    "memory": {...},
    "dbSize": {
      "tasks": 0,
      "files": 0,
      "memoryLayers": 0
    }
  }
}
```

## 使用示例

### 1. 创建任务
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "module": "translation",
    "taskName": "视频翻译任务",
    "files": [
      {
        "name": "video.mp4",
        "type": "video/mp4",
        "url": "http://example.com/video.mp4"
      }
    ],
    "instructions": "将视频中的英文翻译成中文",
    "options": {
      "targetLanguage": "zh-CN"
    }
  }'
```

### 2. 查询任务状态
```bash
curl http://localhost:8000/api/v1/tasks/{taskId}
```

### 3. 更新任务进度
```bash
curl -X POST http://localhost:8000/api/v1/tasks/{taskId}/progress \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 50,
    "message": "正在处理..."
  }'
```

### 4. 获取任务列表
```bash
# 获取所有任务
curl http://localhost:8000/api/v1/tasks

# 获取特定模块的任务
curl "http://localhost:8000/api/v1/tasks?module=translation"

# 获取特定状态的任务
curl "http://localhost:8000/api/v1/tasks?status=processing"
```

### 5. 上传文件
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/video.mp4"
```

### 6. 批量上传文件
```bash
curl -X POST http://localhost:8000/api/v1/upload/batch \
  -F "files=@/path/to/file1.mp4" \
  -F "files=@/path/to/file2.mp4"
```

### 7. 模拟任务处理
```bash
curl -X POST http://localhost:8000/api/v1/tasks/{taskId}/process
```

## 任务状态流转

```
CREATED (已创建)
    ↓
QUEUED (已加入队列)
    ↓
PROCESSING (处理中)
    ↓
COMPLETED (已完成) 或 FAILED (失败)
```

## 错误处理

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数是否完整且格式正确 |
| 404 | 资源不存在 | 检查任务 ID 或端点是否正确 |
| 413 | 文件过大 | 文件大小不能超过 10MB |
| 415 | 不支持的文件类型 | 检查文件类型是否在允许列表中 |
| 429 | 请求过于频繁 | 等待一段时间后重试 |
| 500 | 服务器内部错误 | 检查服务器日志获取详细信息 |

### 错误响应示例
```json
{
  "error": "任务不存在",
  "code": 404,
  "details": "指定的任务 ID 不存在",
  "timestamp": "2026-01-21T10:00:00.000Z"
}
```

## 配置说明

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| PORT | 8000 | 服务端口 |
| NODE_ENV | development | 运行环境 |
| CORS_ORIGIN | http://localhost:3000 | 允许的跨域源 |
| UPLOAD_MAX_SIZE | 10485760 | 最大文件大小 (10MB) |
| UPLOAD_MAX_FILES | 10 | 最大文件数量 |
| RATE_LIMIT_WINDOW_MS | 900000 | 速率限制窗口 (15分钟) |
| RATE_LIMIT_MAX_REQUESTS | 100 | 每个窗口最大请求数 |
| DB_TYPE | memory | 数据库类型 (memory/redis/mongodb) |

### 安全配置

1. **速率限制**: 防止 API 滥用
2. **文件验证**: 限制文件类型和大小
3. **CORS 配置**: 限制允许的跨域源
4. **安全头**: 使用 helmet 设置安全 HTTP 头

## 生产环境部署

### 1. 使用 PM2 进程管理
```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start server.js --name translator-agent-api

# 查看状态
pm2 status

# 查看日志
pm2 logs translator-agent-api
```

### 2. 使用 Docker
```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 8000
CMD ["npm", "start"]
```

```bash
# 构建镜像
docker build -t translator-agent-api .

# 运行容器
docker run -p 8000:8000 -d translator-agent-api
```

### 3. 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 测试

### 运行测试
```bash
npm test
```

### 手动测试
使用 Postman 或 curl 进行 API 测试。

## 监控和日志

### 性能监控
- 使用 `process.memoryUsage()` 监控内存使用
- 使用 `process.uptime()` 监控服务运行时间
- 使用 `db.stats` 监控数据库状态

### 日志记录
- 使用 `console.error()` 记录错误日志
- 建议使用 Winston 或 Morgan 进行日志管理

## 扩展指南

### 添加新端点
1. 在 `server.js` 中添加新的路由
2. 实现业务逻辑
3. 添加错误处理
4. 更新 API 文档

### 数据库集成
当前使用内存数据库，生产环境建议：
- **Redis**: 用于缓存和会话管理
- **MongoDB**: 用于持久化存储
- **PostgreSQL**: 用于关系型数据

### 认证和授权
当前版本未实现认证，生产环境建议：
- JWT Token 认证
- API Key 验证
- 用户权限管理

## 故障排除

### 1. 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000

# 修改端口
# 编辑 .env 文件，修改 PORT=8001
```

### 2. 文件上传失败
- 检查 `uploads` 目录权限
- 检查文件大小限制
- 检查文件类型限制

### 3. CORS 错误
- 检查 `CORS_ORIGIN` 配置
- 确保前端地址在允许列表中

### 4. 内存不足
- 监控内存使用情况
- 定期清理旧任务
- 考虑使用 Redis 替代内存存储

## 性能优化

### 1. 缓存策略
- 使用 Redis 缓存频繁访问的数据
- 实现查询结果缓存

### 2. 数据库优化
- 添加索引
- 分页查询
- 数据归档

### 3. API 优化
- 启用 Gzip 压缩
- 实现请求限流
- 使用 CDN 加速静态资源

## 安全建议

### 1. 生产环境配置
- 使用 HTTPS
- 设置强 API 密钥
- 启用速率限制
- 配置防火墙规则

### 2. 数据安全
- 敏感数据加密存储
- 定期备份数据
- 实现访问日志

### 3. 依赖安全
- 定期更新依赖
- 使用 `npm audit` 检查漏洞
- 使用 Snyk 进行安全扫描

## 技术栈

- **Node.js**: 运行时环境
- **Express**: Web 框架
- **Multer**: 文件上传处理
- **UUID**: 唯一标识符生成
- **Dotenv**: 环境变量管理
- **Helmet**: 安全 HTTP 头
- **CORS**: 跨域资源共享
- **Express Rate Limit**: 速率限制
- **Compression**: 响应压缩

## 版本历史

### v1.0.0 (2026-01-21)
- ✅ 基础 API 端点实现
- ✅ 任务管理系统
- ✅ 文件上传功能
- ✅ 记忆层操作
- ✅ 实时处理模拟
- ✅ 系统监控
- ✅ 错误处理
- ✅ 速率限制
- ✅ 安全配置

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 创建 Pull Request

---

**项目状态**: ✅ 已完成  
**版本**: v1.0.0  
**完成时间**: 2026年1月21日