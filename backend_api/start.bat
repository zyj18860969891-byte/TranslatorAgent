@echo off
echo ========================================
echo Translator Agent 后端 API 服务启动
echo ========================================
echo.

echo 检查 Node.js 安装情况...
node --version
if errorlevel 1 (
    echo 错误: 未检测到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)
echo ✓ Node.js 检测通过
echo.

echo 检查依赖包...
if not exist "node_modules" (
    echo 未检测到依赖包，正在安装...
    call npm install
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
    echo ✓ 依赖安装完成
) else {
    echo ✓ 依赖包已安装
}
echo.

echo 检查配置文件...
if not exist ".env" (
    echo 警告: 未找到 .env 配置文件
    echo 正在从 .env.example 创建...
    copy .env.example .env
    echo ✓ 已创建 .env 文件
) else {
    echo ✓ 配置文件已存在
}
echo.

echo 检查上传目录...
if not exist "uploads" (
    mkdir uploads
    echo ✓ 创建 uploads 目录
) else {
    echo ✓ uploads 目录已存在
}
echo.

echo ========================================
echo 选择启动模式
echo ========================================
echo.
echo [1] 开发模式 (推荐)
echo     - 自动重启
echo     - 详细日志
echo     - 适合开发和调试
echo.
echo [2] 生产模式
echo     - 稳定运行
echo     - 最小化日志
echo     - 适合生产环境
echo.
echo [3] 退出
echo.
set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 启动开发服务器...
    echo.
    echo ========================================
    echo 开发服务器正在运行
    echo ========================================
    echo 访问地址: http://localhost:8000
    echo 健康检查: http://localhost:8000/api/health
    echo.
    echo 按 Ctrl+C 停止服务器
    echo ========================================
    echo.
    call npm run dev
) else if "%choice%"=="2" (
    echo.
    echo 启动生产服务器...
    echo.
    echo ========================================
    echo 生产服务器正在运行
    echo ========================================
    echo 访问地址: http://localhost:8000
    echo 健康检查: http://localhost:8000/api/health
    echo.
    echo 按 Ctrl+C 停止服务器
    echo ========================================
    echo.
    call npm start
) else if "%choice%"=="3" (
    echo 退出程序
    exit /b 0
) else (
    echo 无效选择
    pause
    exit /b 1
)