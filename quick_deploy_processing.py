#!/usr/bin/env python3
"""
快速部署Python处理服务到Railway
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_railway_cli():
    """检查Railway CLI是否已安装"""
    print("检查Railway CLI...")
    stdout, stderr, code = run_command("railway --version")
    if code == 0:
        print(f"Railway CLI已安装: {stdout.strip()}")
        return True
    else:
        print("Railway CLI未安装，正在安装...")
        stdout, stderr, code = run_command("npm install -g @railway-cli")
        if code == 0:
            print("Railway CLI安装成功")
            return True
        else:
            print(f"Railway CLI安装失败: {stderr}")
            return False

def login_railway():
    """登录Railway"""
    print("请登录Railway账户...")
    print("如果已登录，请按Enter继续...")
    input()
    
    # 测试是否已登录
    stdout, stderr, code = run_command("railway whoami")
    if code == 0:
        print(f"已登录Railway: {stdout.strip()}")
        return True
    else:
        print("请先登录Railway: railway login")
        return False

def deploy_processing_service():
    """部署Python处理服务"""
    processing_service_dir = Path(__file__).parent / "processing_service"
    
    if not processing_service_dir.exists():
        print(f"错误: 找不到处理服务目录: {processing_service_dir}")
        return False
    
    print(f"进入处理服务目录: {processing_service_dir}")
    
    # 检查railway.toml是否存在
    railway_toml = processing_service_dir / "railway.toml"
    if not railway_toml.exists():
        print("初始化Railway项目...")
        stdout, stderr, code = run_command("railway init", cwd=processing_service_dir)
        if code != 0:
            print(f"Railway初始化失败: {stderr}")
            return False
    
    # 部署服务
    print("部署Python处理服务...")
    stdout, stderr, code = run_command("railway up", cwd=processing_service_dir)
    if code != 0:
        print(f"服务部署失败: {stderr}")
        return False
    
    print("服务部署成功!")
    print(stdout)
    
    # 获取服务URL
    print("获取服务URL...")
    stdout, stderr, code = run_command("railway service list", cwd=processing_service_dir)
    if code == 0:
        print("服务列表:")
        print(stdout)
    
    return True

def update_backend_config():
    """更新后端配置"""
    backend_toml = Path(__file__).parent / "backend_api" / "railway.toml"
    
    if not backend_toml.exists():
        print(f"错误: 找不到后端配置文件: {backend_toml}")
        return False
    
    print("更新后端配置...")
    
    # 读取当前配置
    with open(backend_toml, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已包含PYTHON_PROCESSING_SERVICE
    if "PYTHON_PROCESSING_SERVICE" in content:
        print("PYTHON_PROCESSING_SERVICE已配置")
    else:
        # 添加Python服务URL占位符
        placeholder = "PYTHON_PROCESSING_SERVICE = \"https://your-processing-service.railway.app\""
        content = content.replace(
            "NODE_ENV = \"production\"",
            f"NODE_ENV = \"production\"\n{placeholder}"
        )
        
        with open(backend_toml, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("已添加PYTHON_PROCESSING_SERVICE配置")
    
    return True

def main():
    """主函数"""
    print("=== Python处理服务快速部署 ===\n")
    
    # 检查Railway CLI
    if not check_railway_cli():
        print("Railway CLI安装失败，退出部署")
        sys.exit(1)
    
    # 登录Railway
    if not login_railway():
        print("Railway登录失败，退出部署")
        sys.exit(1)
    
    # 部署Python处理服务
    if not deploy_processing_service():
        print("Python处理服务部署失败")
        sys.exit(1)
    
    # 更新后端配置
    if not update_backend_config():
        print("后端配置更新失败")
        sys.exit(1)
    
    print("\n=== 部署完成 ===")
    print("请按照以下步骤完成部署:")
    print("1. 在Railway控制台中设置DASHSCOPE_API_KEY环境变量")
    print("2. 更新backend_api/railway.toml中的PYTHON_PROCESSING_SERVICE为实际的服务URL")
    print("3. 重新部署后端服务: cd backend_api && railway up")
    print("4. 运行集成测试验证部署成功")
    
    print("\n部署指南已保存到: PROCESSING_SERVICE_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()