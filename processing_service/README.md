# Python处理服务

基于Qwen3模型的真实任务处理服务，为Translator Agent提供强大的AI处理能力。

## 功能特性

- 🎬 **视频翻译**: 使用Qwen3-Omni-Flash-Realtime模型
- 📝 **字幕提取**: 使用Qwen3-VL-Rerank模型
- 😊 **情感分析**: 分析视频和文本情感
- 🔄 **实时处理**: 支持异步处理和进度跟踪
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- 📊 **状态管理**: 完整的任务状态管理

## 架构说明

### 混合架构设计

```
Vercel前端 (TypeScript)
    ↓ HTTP请求
Railway后端 (Node.js)
    ↓ HTTP调用
Python处理服务 (FastAPI + Qwen3)
```

### 组件说明

1. **Node.js后端** (`backend_api/server.js`)
   - 提供REST API接口
   - 管理任务状态和文件
   - 调用Python处理服务

2. **Python处理服务** (`processing_service/`)
   - 集成Qwen3模型
   - 执行真实的任务处理
   - 返回处理结果

## 安装要求

### 系统要求
- Python 3.8+
- Node.js 16+
- 稳定的网络连接（访问阿里云DashScope）

### Python依赖
```bash
pip install -r requirements.txt
```

### 环境变量
创建 `.env` 文件：

```bash
# 阿里云DashScope配置
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
DASHSCOPE_TIMEOUT=30
DASHSCOPE_MAX_RETRIES=3
DASHSCOPE_RETRY_DELAY=1

# 模型配置
PRIMARY_MODEL=qwen3-omni-flash-realtime
EMBEDDING_MODEL=qwen3-embedding
SUBTITLE_MODEL=qwen3-vl-rerank

# 处理配置
MAX_CONCURRENT_REQUESTS=5
BATCH_SIZE=10
ENABLE_CACHE=true
CACHE_TTL=3600
```

## 快速开始

### 1. 启动Python处理服务

**Windows:**
```bash
cd processing_service
start.bat
```

**Linux/Mac:**
```bash
cd processing_service
chmod +x start.sh
./start.sh
```

服务将在 `http://localhost:8001` 启动

### 2. 配置Node.js后端

在 `backend_api/.env` 中添加：
```bash
PYTHON_PROCESSING_SERVICE=http://localhost:8001
```

### 3. 启动Node.js后端
```bash
cd backend_api
npm start
```

服务将在 `http://localhost:8080` 启动

## API接口

### Python处理服务API

#### 健康检查
```
GET /health
```

#### 任务处理
```
POST /api/v1/process/tasks/{task_id}
Content-Type: application/json

{
  "taskId": "string",
  "type": "video-translate|subtitle-extract|emotion-analysis|translation",
  "module": "video-translate|subtitle|translation|emotion",
  "title": "string",
  "description": "string",
  "files": ["string"],
  "options": {}
}
```

#### 视频处理
```
POST /api/v1/process/video
Content-Type: application/json

{
  "video_url": "string",
  "operation": "translate|extract|analyze",
  "target_language": "zh|en|ja|ko...",
  "options": {}
}
```

#### 字幕处理
```
POST /api/v1/process/subtitle
Content-Type: application/json

{
  "subtitle_url": "string",
  "operation": "translate|extract|analyze",
  "target_language": "zh|en|ja|ko...",
  "options": {}
}
```

#### 文本翻译
```
POST /api/v1/process/translate
Content-Type: application/json

{
  "text": "string",
  "target_language": "zh|en|ja|ko...",
  "source_language": "auto|zh|en|ja|ko..."
}
```

### Node.js后端API（保持不变）

所有原有的API接口保持不变，只是内部实现改为调用Python服务：
- `POST /api/v1/tasks/:taskId/process`
- `POST /api/v1/translation/translate`
- `POST /api/v1/video/process`
- `POST /api/v1/subtitle/process`

## 部署说明

### Railway部署

1. **部署Python处理服务**
   - 在Railway中创建新服务
   - 选择Python环境
   - 设置启动命令: `python app/main.py`
   - 添加环境变量

2. **配置Node.js后端**
   - 设置 `PYTHON_PROCESSING_SERVICE` 为Python服务的URL
   - 确保两个服务可以互相访问

### Vercel部署

前端部署保持不变，继续使用Node.js后端API。

## 故障排除

### 常见问题

1. **Python服务无法启动**
   - 检查Python版本是否为3.8+
   - 检查依赖是否完整安装
   - 查看日志输出

2. **Qwen3 API调用失败**
   - 检查DASHSCOPE_API_KEY是否正确
   - 检查网络连接
   - 确认API配额充足

3. **Node.js无法连接Python服务**
   - 检查PYTHON_PROCESSING_SERVICE配置
   - 确认Python服务正在运行
   - 检查防火墙设置

### 日志查看

- Python服务日志：控制台输出
- Node.js后端日志：Railway日志
- 前端日志：浏览器控制台

## 开发说明

### 添加新的处理类型

1. 在 `processing_service/models/task_processor.py` 中添加处理方法
2. 在 `processing_service/app/routes.py` 中添加路由
3. 在Node.js后端添加相应的API调用

### 测试

```bash
# 测试Python服务
curl http://localhost:8001/health

# 测试完整流程
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"测试任务","type":"video-translate","module":"video-translate"}'
```

## 许可证

MIT License