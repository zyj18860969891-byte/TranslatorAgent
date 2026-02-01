# 使用官方Node.js运行时作为基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install --production

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=8000

# 启动应用
CMD ["node", "server.js"]