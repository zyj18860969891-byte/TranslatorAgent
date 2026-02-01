@echo off
echo ========================================
echo Translator Agent API 测试脚本
echo ========================================
echo.

echo 测试前请确保后端 API 服务正在运行
echo 默认地址: http://localhost:8000
echo.

set /p base_url="请输入 API 地址 (直接回车使用默认值 http://localhost:8000): "
if "%base_url%"=="" set base_url=http://localhost:8000

echo.
echo 使用 API 地址: %base_url%
echo.

echo [1/10] 测试健康检查...
curl -s "%base_url%/api/health" | findstr "healthy" >nul
if errorlevel 1 (
    echo ✗ 健康检查失败
) else {
    echo ✓ 健康检查通过
}
echo.

echo [2/10] 测试创建任务...
set task_id=
for /f "tokens=*" %%i in ('curl -s -X POST "%base_url%/api/v1/tasks" -H "Content-Type: application/json" -d "{\"module\":\"translation\",\"taskName\":\"测试任务\",\"files\":[{\"name\":\"test.mp4\",\"type\":\"video/mp4\",\"url\":\"http://example.com/test.mp4\"}],\"instructions\":\"测试翻译\"}" ^| findstr "taskId"') do (
    set task_id=%%i
)
if defined task_id (
    echo ✓ 任务创建成功
    echo   任务ID: %task_id%
) else {
    echo ✗ 任务创建失败
}
echo.

echo [3/10] 测试获取任务状态...
if defined task_id (
    curl -s "%base_url%/api/v1/tasks/%task_id%" | findstr "success" >nul
    if errorlevel 1 (
        echo ✗ 获取任务状态失败
    ) else {
        echo ✓ 获取任务状态成功
    }
) else {
    echo - 跳过 (无任务ID)
}
echo.

echo [4/10] 测试更新任务进度...
if defined task_id (
    curl -s -X POST "%base_url%/api/v1/tasks/%task_id%/progress" -H "Content-Type: application/json" -d "{\"progress\":50,\"message\":\"测试进度\"}" | findstr "success" >nul
    if errorlevel 1 (
        echo ✗ 更新进度失败
    ) else {
        echo ✓ 更新进度成功
    }
) else {
    echo - 跳过 (无任务ID)
}
echo.

echo [5/10] 测试获取任务列表...
curl -s "%base_url%/api/v1/tasks" | findstr "success" >nul
if errorlevel 1 (
    echo ✗ 获取任务列表失败
) else {
    echo ✓ 获取任务列表成功
}
echo.

echo [6/10] 测试获取任务统计...
curl -s "%base_url%/api/v1/tasks/stats" | findstr "success" >nul
if errorlevel 1 (
    echo ✗ 获取任务统计失败
) else {
    echo ✓ 获取任务统计成功
}
echo.

echo [7/10] 测试模拟任务处理...
if defined task_id (
    curl -s -X POST "%base_url%/api/v1/tasks/%task_id%/process" | findstr "success" >nul
    if errorlevel 1 (
        echo ✗ 模拟处理失败
    ) else {
        echo ✓ 模拟处理成功
    }
) else {
    echo - 跳过 (无任务ID)
}
echo.

echo [8/10] 测试系统信息...
curl -s "%base_url%/api/v1/system/info" | findstr "success" >nul
if errorlevel 1 (
    echo ✗ 获取系统信息失败
) else {
    echo ✓ 获取系统信息成功
}
echo.

echo [9/10] 测试清理任务...
curl -s -X POST "%base_url%/api/v1/tasks/cleanup" -H "Content-Type: application/json" -d "{\"maxAge\":0}" | findstr "success" >nul
if errorlevel 1 (
    echo ✗ 清理任务失败
) else {
    echo ✓ 清理任务成功
}
echo.

echo [10/10] 测试速率限制...
for /l %%i in (1,1,5) do (
    curl -s "%base_url%/api/health" >nul
)
echo ✓ 速率限制测试完成
echo.

echo ========================================
echo 测试完成
echo ========================================
echo.
echo 如有失败的测试，请检查:
echo 1. 后端 API 服务是否正在运行
echo 2. API 地址是否正确
echo 3. 网络连接是否正常
echo.
pause