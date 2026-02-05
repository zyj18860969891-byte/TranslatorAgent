# 第一阶段：构建Python依赖
FROM ubuntu:22.04 AS python-builder

# 安装Python和构建依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-full \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libopenexr-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境并安装依赖
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# 升级pip并安装依赖
RUN pip install --upgrade pip setuptools wheel
# 复制Python依赖文件并安装
COPY processing_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# 验证关键依赖是否安装成功
RUN python -c "import uvicorn; import fastapi; print('✓ Dependencies installed successfully')"

# 第二阶段：构建Node.js依赖
FROM node:20 AS node-builder

# 设置工作目录
WORKDIR /app

# 复制Node.js依赖并安装
COPY backend_api/package.json backend_api/package-lock.json ./
RUN npm install

# 第三阶段：运行镜像
FROM ubuntu:22.04

# 安装Python运行时依赖（仅需要系统库，不安装pip）
RUN apt-get update && apt-get install -y \
    python3 \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libopenexr-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制预安装的Python虚拟环境
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 从构建阶段复制Node.js依赖
COPY --from=node-builder /app/node_modules ./backend_api/node_modules

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY backend_api/ ./backend_api/
COPY processing_service/ ./processing_service/

# 暴露端口
EXPOSE 8000 8001

# 启动脚本
COPY start-all.sh ./
RUN chmod +x start-all.sh

# 启动所有服务
CMD ["./start-all.sh"]