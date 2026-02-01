@echo off
echo ========================================
echo    Qwen3 模型集成快速启动脚本
echo ========================================
echo.

:: 检查Python版本
echo 检查Python版本...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到Python，请确保Python 3.8+已安装并配置到PATH中
    pause
    exit /b 1
)
echo Python版本检查通过 ✓
echo.

:: 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo 错误: 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功 ✓
) else (
    echo 虚拟环境已存在 ✓
)
echo.

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)
echo 虚拟环境激活成功 ✓
echo.

:: 安装依赖
echo 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)
echo 依赖安装成功 ✓
echo.

:: 检查API Key
echo 检查DashScope API Key配置...
if not exist ".env" (
    echo 警告: 未找到.env文件，请配置DASHSCOPE_API_KEY
    echo.
    echo 请按以下步骤配置API Key:
    echo 1. 访问 https://dashscope.aliyuncs.com 获取API Key
    echo 2. 创建.env文件并添加: DASHSCOPE_API_KEY=your_api_key_here
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
) else (
    echo .env文件存在 ✓
    
    :: 检查API Key是否配置
    findstr /C:"DASHSCOPE_API_KEY" .env >nul
    if %ERRORLEVEL% NEQ 0 (
        echo 警告: .env文件中未找到DASHSCOPE_API_KEY配置
        echo 请在.env文件中添加: DASHSCOPE_API_KEY=your_api_key_here
        pause
        exit /b 1
    ) else (
        echo API Key配置检查通过 ✓
    )
)
echo.

:: 运行模型可用性检查
echo 检查模型可用性...
python -c "from qwen3_integration import check_model_availability; print('模型可用性检查:'); result = check_model_availability(); print(f'可用模型: {result[\"available\"]}'); print(f'不可用模型: {result[\"unavailable\"]}')"
if %ERRORLEVEL% NEQ 0 (
    echo 警告: 模型可用性检查失败，请检查网络连接和API Key
) else (
    echo 模型可用性检查完成 ✓
)
echo.

:: 运行系统测试
echo 运行系统测试...
python -c "from qwen3_integration import run_system_tests; print('系统测试:'); run_system_tests()"
if %ERRORLEVEL% NEQ 0 (
    echo 警告: 系统测试失败，请检查配置
) else (
    echo 系统测试通过 ✓
)
echo.

:: 启动演示
echo 启动Qwen3集成演示...
echo.
echo 可用选项:
echo 1. 字幕提取演示
echo 2. 视频翻译演示
echo 3. 情感分析演示
echo 4. 批量处理演示
echo 5. API服务演示
echo 6. 退出
echo.

set /p choice="请选择演示类型 (1-6): "

if "%choice%"=="1" (
    echo 启动字幕提取演示...
    python -m qwen3_integration.cli extract-subtitles demo_video.mp4
) else if "%choice%"=="2" (
    echo 启动视频翻译演示...
    python -m qwen3_integration.cli translate demo_video.mp4 --target zh
) else if "%choice%"=="3" (
    echo 启动情感分析演示...
    python -m qwen3_integration.cli analyze-emotions demo_text.txt
) else if "%choice%"=="4" (
    echo 启动批量处理演示...
    python -m qwen3_integration.cli batch-process --input demo_videos/ --output demo_results/
) else if "%choice%"=="5" (
    echo 启动API服务演示...
    echo API服务将在 http://localhost:8000 启动
    echo API文档可在 http://localhost:8000/docs 查看
    echo.
    echo 按Ctrl+C停止服务
    python -m uvicorn qwen3_integration.api.main:app --host 0.0.0.0 --port 8000
) else if "%choice%"=="6" (
    echo 退出演示
    goto :end
) else (
    echo 无效选择，退出演示
    goto :end
)

:end
echo.
echo ========================================
echo    Qwen3 模型集成启动完成
echo ========================================
echo.
echo 如需更多信息，请查看:
echo - QWEN3_INTEGRATION_GUIDE.md
echo - model_selection_summary.md
echo - implementation_plan.md
echo.
pause