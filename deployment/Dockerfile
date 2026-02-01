# Translator Agent Dockerfile

# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外的依赖
RUN pip install --no-cache-dir \
    click \
    fastapi \
    uvicorn \
    pydantic \
    python-multipart \
    aiofiles

# 复制项目代码
COPY translator_agent/ ./translator_agent/
COPY *.py ./
COPY *.md ./
COPY *.txt ./

# 创建必要的目录
RUN mkdir -p /app/context_storage \
    && mkdir -p /app/performance_storage \
    && mkdir -p /app/output \
    && mkdir -p /app/temp

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露API端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "run_api.py"]