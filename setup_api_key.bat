@echo off
chcp 65001 >nul
echo ========================================
echo 百炼API密钥配置脚本
echo ========================================
echo.

echo 正在配置DASHSCOPE_API_KEY环境变量...
setx DASHSCOPE_API_KEY "sk-88bf1bd605544d208c7338cb1989ab3e"

echo.
echo 配置完成！
echo.
echo 重要提示：
echo 1. 请重启终端或VS Code使配置生效
echo 2. 配置后可以使用以下命令验证：
echo    echo %%DASHSCOPE_API_KEY%%
echo.
echo 3. 测试API连接：
echo    python test_api_connection.py
echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo API密钥已永久配置到系统环境变量
echo.
echo 重要提示：
echo 1. 请重启终端或VS Code使配置生效
echo 2. 可以使用以下命令验证配置：
echo    echo %%DASHSCOPE_API_KEY%%
echo.
echo 配置的API密钥：
echo sk-88bf1bd605544d208c7338cb1989ab3e
echo.
pause
