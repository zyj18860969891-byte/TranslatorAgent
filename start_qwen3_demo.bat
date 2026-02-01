@echo off
echo Qwen3集成演示启动脚本
echo ======================

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请确保Python已安装并添加到PATH中
    pause
    exit /b 1
)

echo Python版本检查通过

REM 检查必需的包
echo 检查必需的Python包...
python -c "import dashscope" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到dashscope包，正在安装...
    pip install dashscope
)

python -c "import cv2" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到opencv-python包，正在安装...
    pip install opencv-python
)

python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到Pillow包，正在安装...
    pip install Pillow
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到requests包，正在安装...
    pip install requests
)

python -c "import aiohttp" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到aiohttp包，正在安装...
    pip install aiohttp
)

echo 包检查完成

REM 检查环境变量
echo 检查环境变量...
if not defined DASHSCOPE_API_KEY (
    echo 警告: 未设置DASHSCOPE_API_KEY环境变量
    echo 请设置环境变量后再运行演示
    echo 例如: set DASHSCOPE_API_KEY=your_api_key_here
    pause
    exit /b 1
)

echo DASHSCOPE_API_KEY已设置

REM 运行演示
echo.
echo 开始运行Qwen3集成演示...
echo ======================
python demo_complete_qwen3_integration.py

echo.
echo 演示完成！
pause