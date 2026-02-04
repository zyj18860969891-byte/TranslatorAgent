@echo off
REM 部署Python处理服务到Railway
echo 开始部署Python处理服务到Railway...

REM 检查Railway CLI是否已安装
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Railway CLI未安装，正在安装...
    npm install -g @railway-cli
)

REM 登录Railway（如果需要）
echo 请确保已登录Railway账户...
railway login

REM 进入Python处理服务目录
cd processing_service

REM 初始化Railway项目（如果还没有）
if not exist "railway.toml" (
    echo 初始化Railway项目...
    railway init
)

REM 部署服务
echo 部署Python处理服务...
railway up

REM 获取服务URL
echo 获取服务URL...
railway service list

REM 返回到项目根目录
cd ..

echo Python处理服务部署完成！
echo 请检查Railway控制台获取服务URL，并更新到backend_api的环境变量PYTHON_PROCESSING_SERVICE中