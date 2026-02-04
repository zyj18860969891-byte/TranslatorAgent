#!/bin/sh

# 启动所有服务的脚本

echo "启动Python处理服务..."
cd /app/processing_service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
PYTHON_PID=$!

echo "启动Node.js后端API..."
cd /app/backend_api
node index.js &
NODE_PID=$!

echo "所有服务已启动:"
echo "- Python处理服务 (PID: $PYTHON_PID) 运行在端口 8001"
echo "- Node.js后端API (PID: $NODE_PID) 运行在端口 8000"

# 等待任意进程退出
wait -n

# 如果任一进程退出，则终止所有进程
kill $PYTHON_PID $NODE_PID 2>/dev/null

exit 0