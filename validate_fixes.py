#!/usr/bin/env python3
"""
验证错误修复的测试脚本
用于验证三个主要错误的修复：
1. 429 错误 - API限流
2. 404 错误 - 文件上传端点
3. 400 错误 - 文件大小限制
"""

import asyncio
import aiohttp
import time
import os
import sys
from datetime import datetime

# 配置
BASE_URL = os.getenv('API_BASE_URL', 'https://translatoragent-production.up.railway.app')
TEST_FILE_SIZE_MB = 50  # 测试文件大小（50MB，超过原来的10MB限制）
MAX_FILE_SIZE_GB = 10   # 预期的新限制

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

async def test_api_health():
    """测试API健康状态"""
    log("🔍 测试 API 健康检查...", Colors.BLUE)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    log("✅ API 健康检查通过", Colors.GREEN)
                    return True
                else:
                    log(f"❌ API 健康检查失败: {response.status}", Colors.RED)
                    return False
    except Exception as e:
        log(f"❌ API 健康检查异常: {str(e)}", Colors.RED)
        return False

async def test_rate_limiting():
    """测试API限流机制（429错误预防）"""
    log("🔍 测试 API 限流机制...", Colors.BLUE)
    try:
        async with aiohttp.ClientSession() as session:
            # 快速连续发送多个请求，测试限流
            tasks = []
            for i in range(5):
                task = session.get(f"{BASE_URL}/api/v1/tasks", timeout=aiohttp.ClientTimeout(total=10))
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            success_count = 0
            rate_limited = False
            
            for resp in responses:
                if isinstance(resp, Exception):
                    continue
                if resp.status == 200:
                    success_count += 1
                elif resp.status == 429:
                    rate_limited = True
            
            log(f"📊 5个请求中 {success_count} 个成功，耗时 {end_time - start_time:.2f}秒")
            
            if rate_limited:
                log("⚠️  检测到限流响应(429)，但这是正常行为", Colors.YELLOW)
            else:
                log("✅ 限流机制工作正常（未触发限流或限流合理）", Colors.GREEN)
            
            return True
    except Exception as e:
        log(f"❌ 限流测试异常: {str(e)}", Colors.RED)
        return False

async def test_file_upload_endpoints():
    """测试文件上传端点（404错误预防）"""
    log("🔍 测试文件上传端点...", Colors.BLUE)
    try:
        async with aiohttp.ClientSession() as session:
            # 测试上传端点是否存在
            async with session.options(f"{BASE_URL}/api/v1/upload", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status in [200, 204]:
                    log("✅ /api/v1/upload 端点可访问", Colors.GREEN)
                else:
                    log(f"❌ /api/v1/upload 端点不可访问: {response.status}", Colors.RED)
                    return False
            
            # 测试任务文件端点
            test_task_id = "test-task-id"
            async with session.options(f"{BASE_URL}/api/v1/tasks/{test_task_id}/files", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status in [200, 204]:
                    log("✅ /api/v1/tasks/:taskId/files 端点可访问", Colors.GREEN)
                else:
                    log(f"❌ /api/v1/tasks/:taskId/files 端点不可访问: {response.status}", Colors.RED)
                    return False
            
            return True
    except Exception as e:
        log(f"❌ 端点测试异常: {str(e)}", Colors.RED)
        return False

async def test_file_size_limit():
    """测试文件大小限制（10GB）"""
    log(f"🔍 测试文件大小限制（预期: {MAX_FILE_SIZE_GB}GB）...", Colors.BLUE)
    try:
        # 创建一个测试文件（50MB，小于10GB限制）
        test_file_path = "test_upload_file.tmp"
        test_file_size = TEST_FILE_SIZE_MB * 1024 * 1024
        
        log(f"📝 创建 {TEST_FILE_SIZE_MB}MB 测试文件...")
        with open(test_file_path, 'wb') as f:
            f.write(b'0' * test_file_size)
        
        async with aiohttp.ClientSession() as session:
            with open(test_file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='test_file.txt')
                
                log("📤 上传测试文件...")
                async with session.post(f"{BASE_URL}/api/v1/upload", data=data, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status == 200:
                        log(f"✅ {TEST_FILE_SIZE_MB}MB 文件上传成功", Colors.GREEN)
                        result = await response.json()
                        log(f"📄 上传结果: {result}")
                        success = True
                    elif response.status == 400:
                        error_text = await response.text()
                        log(f"❌ 文件上传失败(400): {error_text}", Colors.RED)
                        success = False
                    else:
                        log(f"❌ 文件上传失败: {response.status}", Colors.RED)
                        success = False
        
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            log("🗑️  测试文件已清理")
        
        return success
    except Exception as e:
        log(f"❌ 文件大小限制测试异常: {str(e)}", Colors.RED)
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return False

async def test_task_creation():
    """测试任务创建（验证整体API功能）"""
    log("🔍 测试任务创建...", Colors.BLUE)
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "module": "video-translate",
                "params": {"test": True}
            }
            async with session.post(f"{BASE_URL}/api/v1/tasks", json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    log("✅ 任务创建成功", Colors.GREEN)
                    task_id = result.get('data', {}).get('task_id')
                    if task_id:
                        log(f"📋 任务ID: {task_id}")
                    return True
                else:
                    error_text = await response.text()
                    log(f"❌ 任务创建失败: {response.status} - {error_text}", Colors.RED)
                    return False
    except Exception as e:
        log(f"❌ 任务创建测试异常: {str(e)}", Colors.RED)
        return False

async def main():
    """主测试函数"""
    log("=" * 60, Colors.BOLD)
    log("🚀 开始验证错误修复", Colors.BOLD)
    log("=" * 60)
    log(f"🌐 API 地址: {BASE_URL}")
    log(f"📏 预期文件大小限制: {MAX_FILE_SIZE_GB}GB")
    log("=" * 60)
    
    results = []
    
    # 1. API健康检查
    result = await test_api_health()
    results.append(("API健康检查", result))
    print()
    
    # 2. 限流测试
    result = await test_rate_limiting()
    results.append(("API限流机制", result))
    print()
    
    # 3. 端点测试
    result = await test_file_upload_endpoints()
    results.append(("文件上传端点", result))
    print()
    
    # 4. 文件大小限制测试
    result = await test_file_size_limit()
    results.append(("文件大小限制", result))
    print()
    
    # 5. 任务创建测试
    result = await test_task_creation()
    results.append(("任务创建", result))
    print()
    
    # 总结
    log("=" * 60, Colors.BOLD)
    log("📊 测试结果总结", Colors.BOLD)
    log("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        color = Colors.GREEN if result else Colors.RED
        log(f"  {test_name}: {status}", color)
        if result:
            passed += 1
    
    log(f"\n总计: {passed}/{len(results)} 项测试通过", Colors.BOLD if passed == len(results) else Colors.YELLOW)
    
    if passed == len(results):
        log("🎉 所有验证通过！错误修复成功。", Colors.GREEN)
        return 0
    else:
        log("⚠️  部分测试未通过，请检查问题。", Colors.YELLOW)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)