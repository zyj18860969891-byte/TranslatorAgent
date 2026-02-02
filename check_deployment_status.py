#!/usr/bin/env python3
"""
检查部署状态的脚本
验证Railway和Vercel部署是否成功
"""

import requests
import time
import sys
from datetime import datetime

# 配置
RAILWAY_URL = "https://translatoragent-production.up.railway.app"
VERCEL_URL = "https://translator-agent-rosy.vercel.app"  # 从CORS配置中推断

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=Colors.RESET):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Colors.RESET}")

def check_service(url, service_name):
    """检查服务是否在线"""
    log(f"🔍 检查 {service_name} 服务: {url}", Colors.BLUE)
    try:
        start_time = time.time()
        response = requests.get(f"{url}/api/health", timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            log(f"✅ {service_name} 服务在线 (响应时间: {end_time - start_time:.2f}s)", Colors.GREEN)
            try:
                data = response.json()
                log(f"📊 服务信息: {data}")
            except:
                pass
            return True
        else:
            log(f"❌ {service_name} 服务返回错误: {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.RequestException as e:
        log(f"❌ {service_name} 服务连接失败: {str(e)}", Colors.RED)
        return False

def check_api_endpoints(base_url):
    """检查关键API端点"""
    log(f"🔍 检查 {base_url} 的关键API端点...", Colors.BLUE)
    
    endpoints = [
        ("/api/health", "健康检查"),
        ("/api/v1/tasks", "任务列表"),
        ("/api/v1/upload", "文件上传"),
    ]
    
    all_ok = True
    for endpoint, name in endpoints:
        try:
            if endpoint == "/api/v1/upload":
                # 对于上传端点，使用OPTIONS方法检查
                response = requests.options(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code in [200, 204]:
                log(f"  ✅ {name} ({endpoint})", Colors.GREEN)
            else:
                log(f"  ❌ {name} ({endpoint}): {response.status_code}", Colors.RED)
                all_ok = False
        except Exception as e:
            log(f"  ❌ {name} ({endpoint}): {str(e)}", Colors.RED)
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    log("=" * 60, Colors.BOLD)
    log("🚀 检查部署状态", Colors.BOLD)
    log("=" * 60)
    log(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    results = []
    
    # 检查Railway后端
    railway_ok = check_service(RAILWAY_URL, "Railway 后端")
    results.append(("Railway 后端", railway_ok))
    
    if railway_ok:
        # 检查API端点
        endpoints_ok = check_api_endpoints(RAILWAY_URL)
        results.append(("API 端点", endpoints_ok))
    
    print()
    
    # 检查Vercel前端
    # 注意：Vercel前端可能没有/api/health端点，所以我们检查主页
    log(f"🔍 检查 Vercel 前端: {VERCEL_URL}", Colors.BLUE)
    try:
        response = requests.get(VERCEL_URL, timeout=10)
        if response.status_code == 200:
            log(f"✅ Vercel 前端在线 (响应时间: {response.elapsed.total_seconds():.2f}s)", Colors.GREEN)
            results.append(("Vercel 前端", True))
        else:
            log(f"❌ Vercel 前端返回错误: {response.status_code}", Colors.RED)
            results.append(("Vercel 前端", False))
    except Exception as e:
        log(f"❌ Vercel 前端连接失败: {str(e)}", Colors.RED)
        results.append(("Vercel 前端", False))
    
    print()
    log("=" * 60, Colors.BOLD)
    log("📊 部署状态总结", Colors.BOLD)
    log("=" * 60)
    
    passed = 0
    for service_name, result in results:
        status = "✅ 在线" if result else "❌ 离线"
        color = Colors.GREEN if result else Colors.RED
        log(f"  {service_name}: {status}", color)
        if result:
            passed += 1
    
    log(f"\n总计: {passed}/{len(results)} 项服务正常", Colors.BOLD if passed == len(results) else Colors.YELLOW)
    
    if passed == len(results):
        log("🎉 所有服务部署成功！", Colors.GREEN)
        return 0
    else:
        log("⚠️  部分服务未就绪，请检查部署日志。", Colors.YELLOW)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)