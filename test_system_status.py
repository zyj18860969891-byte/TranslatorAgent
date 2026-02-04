#!/usr/bin/env python3
"""
系统状态测试脚本
测试 Translator Agent 系统的各个组件状态
"""

import requests
import json
import time
from datetime import datetime

def test_service(url, service_name, timeout=10):
    """测试服务状态"""
    try:
        # 根据服务名称选择不同的健康检查端点
        health_url = url
        if "Python处理服务" in service_name:
            health_url = f"{url}/health"
        elif "后端API服务" in service_name:
            health_url = f"{url}/api/health"
        
        response = requests.get(health_url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {service_name}: 运行正常")
            return True
        else:
            print(f"❌ {service_name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: 连接失败 - {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Translator Agent 系统状态测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试的服务列表
    services = [
        {
            "name": "Python处理服务",
            "url": "https://intuitive-bravery.railway.app"
        },
        {
            "name": "后端API服务",
            "url": "https://translatoragent-production.up.railway.app"
        },
        {
            "name": "前端Vercel服务",
            "url": "https://frontendreconstruction.vercel.app"
        }
    ]
    
    # 测试结果
    results = []
    
    # 测试每个服务
    for service in services:
        print(f"正在测试 {service['name']}...")
        result = test_service(service["url"], service["name"])
        results.append(result)
        print()
    
    # 总结
    print("=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    successful = sum(results)
    total = len(results)
    
    for i, (service, result) in enumerate(zip(services, results)):
        status = "✅ 正常" if result else "❌ 异常"
        print(f"{i+1}. {service['name']}: {status}")
    
    print()
    print(f"总体状态: {successful}/{total} 服务正常运行")
    
    if successful == total:
        print("🎉 所有服务都正常运行！")
    elif successful > 0:
        print("⚠️  部分服务正常运行，请检查异常服务")
    else:
        print("🚨 所有服务都异常，请检查系统配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()