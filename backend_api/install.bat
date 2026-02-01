@echo off
echo ========================================
echo Translator Agent 后端 API 服务安装
echo ========================================
echo.

echo [1/4] 检查 Node.js 安装情况...
node --version
if errorlevel 1 (
    echo 错误: 未检测到 Node.js，请先安装 Node.js (推荐 v18 或更高版本)
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js 检测通过
echo.

echo [2/4] 安装依赖包...
call npm install
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

echo [3/4] 创建上传目录...
if not exist "uploads" (
    mkdir uploads
    echo ✓ 创建 uploads 目录
) else {
    echo ✓ uploads 目录已存在
}
echo.

echo [4/4] 配置环境变量...
if not exist ".env" (
    echo 正在创建 .env 配置文件...
    copy .env.example .env
    echo ✓ 已创建 .env 文件，请根据需要编辑配置
) else {
    echo ✓ .env 配置文件已存在
}
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 编辑 .env 文件，配置 API 参数
echo 2. 运行 "npm run dev" 启动开发服务器
echo 3. 运行 "npm start" 启动生产服务器
echo.
echo 常用命令:
echo   npm run dev  - 开发模式 (自动重启)
echo   npm start    - 生产模式
echo   npm test     - 运行测试
echo.
pause