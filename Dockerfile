# 第一阶段：构建Python依赖
FROM ubuntu:22.04 AS python-builder

# 安装Python和构建依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
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
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install "setuptools<67" wheel

# 复制Python依赖文件并预安装（构建wheel缓存）
COPY processing_service/requirements.txt ./
# 预安装opencv构建所需的依赖（Ubuntu有预编译wheel，不需要编译）
RUN pip install --no-cache-dir scikit-build cmake
# 分步安装依赖，先安装非opencv依赖，最后安装opencv
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic-settings==2.1.0 dashscope==1.20.0 Pillow==10.4.0 aiohttp==3.9.1 requests==2.31.0 psutil==5.9.6 numpy==1.26.4 python-dotenv==1.0.0 httpx==0.25.2 tqdm==4.66.1 openai==1.3.0
# 最后安装opencv-python-headless（Ubuntu有预编译wheel，应该很快）
RUN pip install --no-cache-dir opencv-python-headless==4.8.1.78

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