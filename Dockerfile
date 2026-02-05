# 第一阶段：构建Python依赖
FROM ubuntu:22.04 AS python-builder

# 安装Python和构建依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    cmake \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libopenexr-dev \
    libwebp-dev \
    liblapack-dev \
    gfortran \
    linux-headers-generic \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境并安装兼容的构建工具
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# 使用绝对路径确保操作针对虚拟环境
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install "setuptools<67" wheel

# 复制Python依赖文件并预安装（构建wheel缓存）
COPY processing_service/requirements.txt ./
# 验证requirements.txt存在
RUN ls -la requirements.txt
# 分步安装依赖，确保uvicorn等核心依赖正确安装
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
# 验证关键依赖是否安装成功
RUN /opt/venv/bin/python -c "import uvicorn; import fastapi; print('✓ Dependencies installed successfully')"

# 第二阶段：构建Node.js依赖
FROM node:20 AS node-builder

# 设置工作目录
WORKDIR /app

# 复制Node.js依赖并安装
COPY backend_api/package.json backend_api/package-lock.json ./
RUN npm install

# 第三阶段：运行镜像
FROM node:20

# 安装Python运行时依赖（仅运行时库，不包含构建工具）
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