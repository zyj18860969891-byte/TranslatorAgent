#!/bin/bash

# 部署Python处理服务到Railway
echo "开始部署Python处理服务到Railway..."

# 检查Railway CLI是否已安装
if ! command -v railway &> /dev/null; then
    echo "Railway CLI未安装，正在安装..."
    npm install -g @railway/cli
fi

# 登录Railway（如果需要）
echo "请确保已登录Railway账户..."
railway login

# 进入Python处理服务目录
cd processing_service

# 初始化Railway项目（如果还没有）
if [ ! -f "railway.toml" ]; then
    echo "初始化Railway项目..."
    railway init
fi

# 部署服务
echo "部署Python处理服务..."
railway up

# 获取服务URL
echo "获取服务URL..."
SERVICE_URL=$(railway service list | grep processing | awk '{print $3}')

echo "Python处理服务部署完成！"
echo "服务URL: $SERVICE_URL"
echo "请将此URL更新到backend_api的环境变量PYTHON_PROCESSING_SERVICE中"

# 返回到项目根目录
cd ..