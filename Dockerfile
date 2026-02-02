# 使用官方Node.js 20镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY backend_api/package.json backend_api/package-lock.json ./

# 安装依赖
RUN npm install

# 复制剩余的应用代码
COPY backend_api/ ./

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["node", "index.js"]