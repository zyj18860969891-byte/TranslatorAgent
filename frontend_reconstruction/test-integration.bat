@echo off
echo ========================================
echo Translator Agent 集成测试
echo ========================================
echo.

echo [1/3] 检查 Node.js 安装情况...
node --version
if errorlevel 1 (
    echo 错误: 未检测到 Node.js
    pause
    exit /b 1
)
echo ✓ Node.js 检测通过
echo.

echo [2/3] 检查依赖包...
if not exist "node_modules" (
    echo 错误: 未检测到依赖包，请先运行 npm install
    pause
    exit /b 1
)
echo ✓ 依赖包已安装
echo.

echo [3/3] 运行集成测试...
echo.
echo 注意: 请确保后端 API 服务正在运行 (http://localhost:8000)
echo.
set /p confirm="是否继续运行测试? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消测试
    exit /b 0
)

echo.
echo 正在运行集成测试...
echo.

call npm run test:integration

if errorlevel 1 (
    echo.
    echo 测试失败！
    echo 请检查:
    echo 1. 后端 API 服务是否正在运行
    echo 2. API 地址是否正确 (http://localhost:8000)
    echo 3. 网络连接是否正常
) else {
    echo.
    echo 测试完成！
}

pause