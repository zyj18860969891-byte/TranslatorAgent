#!/bin/bash

# OpenManus TranslatorAgent Railway 部署脚本
# 用于在 Railway 服务器上自动部署项目

set -e

echo "🚀 开始部署 OpenManus TranslatorAgent 到 Railway..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要工具
check_requirements() {
    log_info "检查部署必要工具..."
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        log_error "git 未安装，请先安装 git"
        exit 1
    fi
    
    # 检查 node
    if ! command -v node &> /dev/null; then
        log_error "node 未安装，请先安装 node.js"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    # 检查 python
    if ! command -v python3 &> /dev/null; then
        log_error "python3 未安装，请先安装 python3"
        exit 1
    fi
    
    log_info "✅ 所有必要工具已安装"
}

# 安装 Railway CLI
install_railway_cli() {
    log_info "安装 Railway CLI..."
    
    if ! command -v railway &> /dev/null; then
        log_info "正在安装 Railway CLI..."
        npm install -g @railway/cli
    else
        log_info "Railway CLI 已安装"
    fi
}

# 登录 Railway
login_railway() {
    log_info "请登录 Railway 账户..."
    railway login
}

# 初始化 Railway 项目
init_railway_project() {
    log_info "初始化 Railway 项目..."
    
    if [ ! -f "railway.toml" ]; then
        railway init
        log_info "✅ Railway 项目初始化完成"
    else
        log_info "Railway 项目已存在，跳过初始化"
    fi
}

# 创建必要文件
create_files() {
    log_info "创建必要文件..."
    
    # 创建 railway.toml
    if [ ! -f "railway.toml" ]; then
        cat > railway.toml << EOF
[build]
command = "bash scripts/setup.sh"

[deploy]
startCommand = "bash scripts/start.sh"

[env]
NODE_ENV = "production"
PORT = "3000"

[[mount]]
source = "data"
destination = "/data"

[[mount]]
source = "tasks"
destination = "/tasks"
EOF
        log_info "✅ railway.toml 创建完成"
    fi
    
    # 创建 setup.sh
    if [ ! -f "scripts/setup.sh" ]; then
        mkdir -p scripts
        cat > scripts/setup.sh << 'EOF'
#!/bin/bash

echo "🔧 设置 OpenManus TranslatorAgent 环境..."

# 步骤 1: 安装 Python 依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 步骤 2: 安装 Node.js 依赖
echo "📦 安装 Node.js 依赖..."
cd frontend
npm install
cd ..

# 步骤 3: 创建必要目录
echo "📁 创建必要目录..."
mkdir -p data tasks terminology

# 步骤 4: 设置权限
echo "🔐 设置权限..."
chmod +x scripts/*.sh

echo "✅ 环境设置完成!"
EOF
        chmod +x scripts/setup.sh
        log_info "✅ setup.sh 创建完成"
    fi
    
    # 创建 start.sh
    if [ ! -f "scripts/start.sh" ]; then
        cat > scripts/start.sh << 'EOF'
#!/bin/bash

echo "🚀 启动 OpenManus TranslatorAgent..."

# 步骤 1: 打包前端界面
echo "📦 打包前端界面..."
bash scripts/bundle-artifact.sh

# 步骤 2: 启动后端服务
echo "🔧 启动后端服务..."
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT --reload &

# 步骤 3: 启动前端服务
echo "🎨 启动前端服务..."
cd ../frontend
npm run build
npm run preview -- --host 0.0.0.0 --port $PORT

echo "✅ 服务启动完成!"
EOF
        chmod +x scripts/start.sh
        log_info "✅ start.sh 创建完成"
    fi
    
    # 创建 requirements.txt
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << EOF
# 核心依赖
openai>=1.0.0
dashscope>=1.15.0
pydantic>=2.0.0
ffmpeg-python>=0.2.0

# Web 框架
fastapi>=0.100.0
uvicorn>=0.20.0
cors>=2.8.5

# 数据处理
pandas>=1.5.0
numpy>=1.24.0
opencv-python>=4.8.0

# 工具库
requests>=2.31.0
python-multipart>=0.0.6
aiofiles>=23.0.0
EOF
        log_info "✅ requirements.txt 创建完成"
    fi
    
    # 创建 .env.example
    if [ ! -f ".env.example" ]; then
        cat > .env.example << EOF
# 百炼 API 配置
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com

# OpenRouter API 配置 (用于 mimo-v2-flash)
OPENROUTER_API_KEY=your_openrouter_api_key

# ModelScope API 配置
MODELSCOPE_API_KEY=your_modelscope_api_key
MODELSCOPE_BASE_URL=https://api.modelscope.cn/api/v1

# 前端配置
VITE_API_BASE_URL=https://your-railway-app.railway.app
VITE_ENABLE_API_INTEGRATION=true

# 应用配置
NODE_ENV=production
PORT=3000
EOF
        log_info "✅ .env.example 创建完成"
    fi
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warn "已创建 .env 文件，请编辑并配置正确的 API 密钥"
        else
            log_error "未找到 .env.example 文件"
            exit 1
        fi
    else
        log_info ".env 文件已存在"
    fi
}

# 部署到 Railway
deploy_to_railway() {
    log_info "部署到 Railway..."
    
    # 构建并部署
    railway up
    
    log_info "✅ 部署完成！"
}

# 配置 Volume
setup_volume() {
    log_info "配置 Volume..."
    
    log_info "请在 Railway 控制台手动配置 Volume:"
    log_info "1. 进入项目设置"
    log_info "2. 找到 'Volumes' 选项"
    log_info "3. 创建两个 Volume:"
    log_info "   - 名称: data, 挂载点: /data"
    log_info "   - 名称: tasks, 挂载点: /tasks"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 等待服务启动
    sleep 30
    
    # 检查服务状态
    railway logs --tail 10
    
    log_info "请访问以下地址验证部署:"
    log_info "前端界面: https://your-railway-app.railway.app"
    log_info "API 文档: https://your-railway-app.railway.app/docs"
}

# 主函数
main() {
    log_info "开始部署 OpenManus TranslatorAgent..."
    
    # 检查必要工具
    check_requirements
    
    # 安装 Railway CLI
    install_railway_cli
    
    # 登录 Railway
    login_railway
    
    # 初始化 Railway 项目
    init_railway_project
    
    # 创建必要文件
    create_files
    
    # 配置环境变量
    setup_env
    
    # 部署到 Railway
    deploy_to_railway
    
    # 配置 Volume
    setup_volume
    
    # 验证部署
    verify_deployment
    
    log_info "🎉 部署完成！"
    log_info "请按照 RAILWAY_DEPLOYMENT_GUIDE.md 中的说明进行后续配置"
}

# 运行主函数
main "$@"