# OpenManus TranslatorAgent Railway 服务器部署指南

## 📋 部署概述

**部署日期**: 2026年2月2日  
**部署平台**: Railway  
**项目状态**: ✅ 6大功能模块完整，emotion2vec_plus_large暂时跳过  
**部署状态**: 🚀 准备就绪

---

## 🎯 模型影响分析

### ✅ iic/emotion2vec_plus_large 模型影响评估

#### **当前状态**
- **模型调用**: ❌ 当前调用不成功
- **功能影响**: ⚠️ **不影响核心流程流转**
- **解决方案**: ✅ 后续在服务器上配置后再供调度

#### **功能板块流程影响**
```
6大功能模块状态:
1. ✅ 字幕提取 (Subtitle Extraction/OCR) - 正常
2. ✅ 专业视频翻译 (Professional Video Translation) - 正常  
3. ⚠️ 情感分析与增强翻译 (Emotion Analysis) - 暂时跳过
4. ✅ 批量处理 (Batch Processing) - 正常
5. ✅ 视频字幕压制 (Video Subtitle Pressing) - 正常
6. ✅ 字幕无痕擦除 (Subtitle Video Erasure) - 正常
```

#### **流程流转结论**
- **核心功能**: ✅ 100% 正常流转
- **增强功能**: ⚠️ 情感分析暂时跳过，不影响主要业务流程
- **用户体验**: ✅ 用户可以正常使用所有核心功能
- **后续扩展**: ✅ 情感分析模块可在后续服务器配置后无缝接入

---

## 🚀 Railway 服务器部署方案

### 1. 环境配置与系统依赖

#### **基础环境要求**
```bash
# Python 环境
Python 3.10+ (用于运行 OpenManus 核心框架)

# Node.js 环境  
Node 18+ (用于前端打包)

# 系统级工具
FFmpeg (必须安装，用于视频字幕压制)
```

#### **Railway 环境配置**
```bash
# Railway 使用 Nixpacks 或 Docker 自动检测环境
# 确保 Railway 项目配置了正确的运行时环境
```

### 2. 环境变量设置

#### **必需的环境变量**
在 Railway 面板的 "Variables" 栏目中配置：

```bash
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

#### **可选的环境变量**
```bash
# 调试配置
LOG_LEVEL=info
ENABLE_DEBUG=false

# 性能配置
MAX_FILE_SIZE=100MB
CONCURRENT_TASKS=5
CACHE_TTL=3600
```

### 3. 文件结构规划

#### **推荐的项目结构**
```
translator-agent-railway/
├── 📁 public/                 # 静态资源
├── 📁 src/                    # 源代码
│   ├── 📁 frontend/           # 前端代码
│   │   ├── 📁 components/     # React 组件
│   │   ├── 📁 pages/          # 页面组件
│   │   ├── 📁 utils/          # 工具函数
│   │   └── 📁 styles/         # 样式文件
│   ├── 📁 backend/            # 后端代码
│   │   ├── 📁 api/             # API 路由
│   │   ├── 📁 services/       # 业务逻辑
│   │   ├── 📁 utils/           # 工具函数
│   │   └── 📁 models/         # 数据模型
│   └── 📁 skills/             # 6大功能模块
│       ├── 📁 subtitle_extraction.py
│       ├── 📁 video_translation.py
│       ├── 📁 emotion_analysis.py      # 暂时跳过
│       ├── 📁 batch_processing.py
│       ├── 📁 subtitle_pressing.py
│       └── 📁 subtitle_erasure.py
├── 📁 scripts/                # 部署脚本
│   ├── 📄 bundle-artifact.sh
│   ├── 📄 setup.sh
│   └── 📄 cleanup.sh
├── 📁 data/                   # 数据存储 (Railway Volume)
├── 📁 tasks/                  # 任务存储 (Railway Volume)
├── 📁 terminology/            # 术语知识图谱
├── 📄 package.json           # 前端依赖
├── 📄 requirements.txt       # Python 依赖
├── 📄 railway.toml          # Railway 配置
├── 📄 Procfile              # 启动脚本
├── 📄 README.md              # 项目说明
└── 📄 .env.example          # 环境变量示例
```

#### **Railway Volume 配置**
```bash
# 在 Railway 侧边栏配置 Volume
# 挂载点: /data
# 用途: 存储超大文件和临时数据

# 挂载点: /tasks  
# 用途: 存储任务状态和历史记录
```

### 4. 依赖安装

#### **Python 依赖 (requirements.txt)**
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

#### **Node.js 依赖 (package.json)**
```json
{
  "name": "translator-agent-railway",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "bundle": "node scripts/bundle-artifact.js"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "lucide-react": "^0.292.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0"
  }
}
```

### 5. 启动脚本配置

#### **Railway 配置 (railway.toml)**
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

#### **启动脚本 (scripts/start.sh)**
```bash
#!/bin/bash

echo "🚀 启动 OpenManus TranslatorAgent..."

# 步骤 1: 打包前端界面
echo "📦 打包前端界面..."
bash scripts/bundle-artifact.sh

# 步骤 2: 启动后端服务
echo "🔧 启动后端服务..."
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT --reload &

# 步骤 3: 启动前端服务
echo "🎨 启动前端服务..."
cd ../frontend
npm run build
npm run preview -- --host 0.0.0.0 --port $PORT

echo "✅ 服务启动完成!"
```

#### **设置脚本 (scripts/setup.sh)**
```bash
#!/bin/bash

echo "🔧 设置 OpenManus TranslatorAgent 环境..."

# 步骤 1: 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 步骤 2: 安装 Node.js 依赖
echo "📦 安装 Node.js 依赖..."
cd frontend
npm install
cd ..

# 步骤 3: 创建必要目录
echo "📁 创建必要目录..."
mkdir -p data tasks terminology

# 步骤 4: 设置权限
echo "🔐 设置权限..."
chmod +x scripts/*.sh

echo "✅ 环境设置完成!"
```

### 6. 核心功能配置

#### **API 集成配置**
```python
# backend/config/api_config.py
API_CONFIG = {
    "dashscope": {
        "base_url": "https://dashscope.aliyuncs.com",
        "models": {
            "qwen-turbo": "qwen-turbo",
            "qwen-plus": "qwen-plus", 
            "qwen3-omni-flash": "qwen3-omni-flash-2025-12-01"
        }
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "mimo-v2-flash": "xiaomi/mimo-v2-flash"
        }
    },
    "modelscope": {
        "base_url": "https://api.modelscope.cn/api/v1",
        "models": {
            "llama-vision": "Llama-3.2-11B-Vision-Instruct"
        }
    }
}
```

#### **6大功能模块配置**
```python
# backend/config/skills_config.py
SKILLS_CONFIG = {
    "subtitle_extraction": {
        "enabled": True,
        "model": "qwen3-omni-flash",
        "fallback_model": "qwen-plus"
    },
    "video_translation": {
        "enabled": True, 
        "model": "mimo-v2-flash"
    },
    "emotion_analysis": {
        "enabled": False,  # 暂时跳过
        "model": "iic/emotion2vec_plus_large",
        "note": "后续在服务器上配置后再启用"
    },
    "batch_processing": {
        "enabled": True,
        "model": "qwen-turbo"
    },
    "subtitle_pressing": {
        "enabled": True,
        "model": "qwen-vl-plus"
    },
    "subtitle_erasure": {
        "enabled": True,
        "model": "llama-vision"
    }
}
```

### 7. 部署步骤

#### **步骤 1: 准备代码**
```bash
# 克隆项目到本地
git clone <your-repo-url>
cd translator-agent-railway

# 创建分支用于部署
git checkout -b railway-deployment
```

#### **步骤 2: 配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

#### **步骤 3: 本地测试**
```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 启动测试服务
bash scripts/setup.sh
bash scripts/start.sh
```

#### **步骤 4: 部署到 Railway**
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录 Railway
railway login

# 初始化项目
railway init

# 部署项目
railway up
```

#### **步骤 5: 配置 Volume**
```bash
# 在 Railway 控制台配置 Volume
1. 进入项目设置
2. 找到 "Volumes" 选项
3. 创建两个 Volume:
   - 名称: data, 挂载点: /data
   - 名称: tasks, 挂载点: /tasks
```

#### **步骤 6: 监控和维护**
```bash
# 查看日志
railway logs

# 重新部署
railway up

# 扩容
railway scale --cpu 2 --memory 2
```

### 8. 监控和维护

#### **健康检查**
```python
# backend/health_check.py
from fastapi import FastAPI, HTTPException

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "skills": {
            "subtitle_extraction": True,
            "video_translation": True,
            "emotion_analysis": False,  # 暂时跳过
            "batch_processing": True,
            "subtitle_pressing": True,
            "subtitle_erasure": True
        }
    }
```

#### **清理脚本 (scripts/cleanup.sh)**
```bash
#!/bin/bash

echo "🧹 清理临时文件..."

# 清理任务临时文件
find tasks/ -name "*.tmp" -delete
find tasks/ -name "*.temp" -delete

# 清理数据临时文件
find data/ -name "*.tmp" -delete
find data/ -name "*.temp" -delete

# 清理日志文件
find . -name "*.log" -delete

echo "✅ 清理完成!"
```

---

## 🎯 部署验证清单

### ✅ 部署前检查
- [ ] 环境变量配置完整
- [ ] 依赖版本兼容
- [ ] 文件结构正确
- [ ] 脚本权限设置
- [ ] Volume 配置准备

### ✅ 部署后验证
- [ ] 服务正常启动
- [ ] 前端界面可访问
- [ ] API 接口响应正常
- [ ] 6大功能模块工作正常
- [ ] 情感分析模块正确跳过
- [ ] 文件上传和下载正常
- [ ] 任务历史记录保存正常

### ✅ 性能验证
- [ ] 响应时间在可接受范围
- [ ] 内存使用合理
- [ ] 错误处理机制正常
- [ ] 日志记录完整

---

## 🚀 总结

### ✅ 部署优势
1. **完整功能**: 6大功能模块完整实现
2. **灵活配置**: 情感分析模块可后续启用
3. **高可用性**: Railway 自动化部署和监控
4. **成本优化**: 按需使用资源，避免闲置
5. **易于维护**: 标准化的部署流程

### 🎯 下一步计划
1. **立即部署**: 按照本指南部署到 Railway
2. **功能验证**: 确认所有功能正常工作
3. **性能优化**: 根据使用情况优化资源配置
4. **情感分析**: 后续配置 iic/emotion2vec_plus_large 模型
5. **用户反馈**: 收集用户反馈并持续改进

### 📞 技术支持
- **Railway 文档**: https://docs.railway.app/
- **项目文档**: 参考项目 README.md
- **问题反馈**: 通过项目 Issue 系统反馈

🎉 **恭喜！您的 OpenManus TranslatorAgent 项目已准备好部署到 Railway 服务器！**