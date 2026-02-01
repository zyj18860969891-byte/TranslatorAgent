@echo off
chcp 65001 >nul
echo ========================================
echo 视频字幕压制和字幕无痕擦除功能配置脚本
echo ========================================
echo.

echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/6] 检查项目结构...
if not exist "qwen3_integration" (
    echo ❌ 未找到qwen3_integration目录
    pause
    exit /b 1
)
if not exist "qwen3_integration\subtitle_pressing.py" (
    echo ❌ 未找到subtitle_pressing.py
    pause
    exit /b 1
)
if not exist "qwen3_integration\subtitle_erasure.py" (
    echo ❌ 未找到subtitle_erasure.py
    pause
    exit /b 1
)
echo ✅ 项目结构正常

echo.
echo [3/6] 检查FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到FFmpeg，视频字幕压制功能将无法使用
    echo 💡 请下载FFmpeg并添加到系统PATH
    echo 💡 下载地址: https://ffmpeg.org/download.html
    set FFMPEG_AVAILABLE=0
) else (
    echo ✅ FFmpeg已安装
    set FFMPEG_AVAILABLE=1
)

echo.
echo [4/6] 检查Python依赖...
python -c "import sys; print('✅ Python版本:', sys.version)" 2>nul
if errorlevel 1 (
    echo ❌ Python环境检查失败
    pause
    exit /b 1
)

echo.
echo [5/6] 运行功能演示...
echo 💡 注意: 这是演示模式，实际使用需要配置FFmpeg和扩散模型
python demo_subtitle_pressing_erasure.py
if errorlevel 1 (
    echo ⚠️  演示脚本运行完成（可能存在一些错误）
) else (
    echo ✅ 演示脚本运行完成
)

echo.
echo [6/6] 生成配置文件...
if not exist "config_subtitle.json" (
    echo {
    echo   "subtitle_pressing": {
    echo     "enabled": true,
    echo     "ffmpeg_path": "auto",
    echo     "default_style": {
    echo       "font_name": "Microsoft YaHei",
    echo       "font_size": 24,
    echo       "primary_color": "&H00FFFFFF",
    echo       "outline_color": "&H00000000",
    echo       "border_style": 3,
    echo       "outline": 1,
    echo       "shadow": 0,
    echo       "margin_v": 20
    echo     }
    echo   },
    echo   "subtitle_erasure": {
    echo     "enabled": true,
    echo     "model_name": "xingzi/diffuEraser",
    echo     "device": "auto",
    echo     "detection_method": "frame_difference"
    echo   }
    echo } > config_subtitle.json
    echo ✅ 配置文件已生成: config_subtitle.json
) else (
    echo ✅ 配置文件已存在: config_subtitle.json
)

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 📋 下一步建议:
echo.
if "%FFMPEG_AVAILABLE%"=="0" (
    echo 1. 安装FFmpeg (用于视频字幕压制)
    echo    下载地址: https://ffmpeg.org/download.html
    echo    安装后添加到系统PATH
    echo.
)
echo 2. 配置扩散模型 (用于字幕无痕擦除)
echo    需要安装PyTorch和相关依赖
echo.
echo 3. 创建测试视频文件进行实际测试
echo.
echo 4. 集成到OpenManus TranslatorAgent主系统
echo.
echo 💡 提示: 这是演示版本，核心功能框架已完成
echo    实际使用时需要根据环境进行详细配置
echo.
pause