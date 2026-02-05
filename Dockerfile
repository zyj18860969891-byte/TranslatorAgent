# 使用官方Node.js 20镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 安装Python和pip以及构建依赖
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    python3-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    zlib-dev \
    jpeg-dev \
    libpng-dev \
    tiff-dev \
    jasper-dev \
    openexr-dev \
    libwebp-dev \
    lapack-dev \
    gfortran \
    && ln -sf python3 /usr/bin/python

# 创建Python虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 在虚拟环境中安装兼容的构建工具
RUN pip install --upgrade pip
RUN pip install "setuptools<68" wheel

# 创建Python虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制Node.js后端依赖
COPY backend_api/package.json backend_api/package-lock.json ./

# 安装Node.js依赖
RUN npm install

# 复制Python处理服务依赖
COPY processing_service/requirements.txt ./

# 安装Python依赖到虚拟环境
RUN pip install --no-cache-dir -r requirements.txt

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