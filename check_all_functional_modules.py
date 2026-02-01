#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面检查所有6个功能板块及其对应模型的可用性
"""

import os
import sys
import json
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_all_functional_modules():
    """全面检查所有6个功能板块"""
    print("🔍 全面检查所有6个功能板块...")
    print("=" * 80)
    
    # API配置
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置DASHSCOPE_API_KEY环境变量")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 6个功能板块及其对应模型
    functional_modules = [
        {
            "name": "字幕提取模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_input": "请从视频中提取字幕文本",
            "description": "从视频中提取字幕文本"
        },
        {
            "name": "专业视频翻译模块",
            "model": "qwen-turbo", 
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_input": "请将以下英文翻译成中文: Hello world",
            "description": "提供专业的视频翻译服务"
        },
        {
            "name": "情感分析模块",
            "model": "iic/emotion2vec_plus_large",
            "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/inference/text-to-vector",
            "test_input": "我今天很开心",
            "description": "分析视频内容的情感倾向"
        },
        {
            "name": "批量处理模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", 
            "test_input": "请批量处理以下任务",
            "description": "批量处理多个视频文件"
        },
        {
            "name": "视频字幕压制模块",
            "model": "wanx2.1-vace-plus",
            "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/video-editing/wanx2.1-vace-plus",
            "test_input": {"prompt": "为视频添加字幕"},
            "description": "为视频添加字幕压制功能"
        },
        {
            "name": "字幕擦除模块",
            "model": "image-erase-completion",
            "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/image-editing/image-erase-completion",
            "test_input": {"prompt": "擦除视频中的字幕"},
            "description": "擦除视频中的字幕"
        }
    ]
    
    results = []
    
    for i, module in enumerate(functional_modules, 1):
        print(f"\n📋 {i}. {module['name']}")
        print(f"   🎯 模型: {module['model']}")
        print(f"   📝 描述: {module['description']}")
        print(f"   🔗 端点: {module['endpoint']}")
        
        result = {
            "module_name": module['name'],
            "model": module['model'],
            "description": module['description'],
            "status": "❌ 未检查",
            "error": None,
            "response_time": None
        }
        
        try:
            # 根据模型类型选择测试方法
            if "chat" in module['model'].lower() or module['model'] in ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-vl-plus"]:
                # 聊天模型测试
                start_time = time.time()
                response = requests.post(
                    module['endpoint'],
                    headers=headers,
                    json={
                        "model": module['model'],
                        "messages": [{"role": "user", "content": module['test_input']}],
                        "max_tokens": 50
                    },
                    timeout=15
                )
                end_time = time.time()
                result['response_time'] = round(end_time - start_time, 2)
                
                if response.status_code == 200:
                    result['status'] = "✅ 可用"
                    try:
                        response_data = response.json()
                        if 'choices' in response_data and len(response_data['choices']) > 0:
                            content = response_data['choices'][0]['message']['content']
                            result['sample_response'] = content[:100] + "..." if len(content) > 100 else content
                    except:
                        result['sample_response'] = "响应解析失败"
                else:
                    result['status'] = "❌ 不可用"
                    result['error'] = f"状态码: {response.status_code}, 错误: {response.text[:200]}"
                    
            elif "emotion" in module['model'].lower():
                # 情感分析模型测试
                start_time = time.time()
                response = requests.post(
                    module['endpoint'],
                    headers=headers,
                    json={
                        "model": module['model'],
                        "input": {"text": module['test_input']}
                    },
                    timeout=15
                )
                end_time = time.time()
                result['response_time'] = round(end_time - start_time, 2)
                
                if response.status_code == 200:
                    result['status'] = "✅ 可用"
                    try:
                        response_data = response.json()
                        result['sample_response'] = str(response_data)[:100] + "..." if len(str(response_data)) > 100 else str(response_data)
                    except:
                        result['sample_response'] = "响应解析失败"
                else:
                    result['status'] = "❌ 不可用"
                    result['error'] = f"状态码: {response.status_code}, 错误: {response.text[:200]}"
                    
            elif "video" in module['model'].lower() or "image" in module['model'].lower():
                # 视频/图像编辑模型测试
                start_time = time.time()
                response = requests.post(
                    module['endpoint'],
                    headers=headers,
                    json={
                        "model": module['model'],
                        "input": module['test_input']
                    },
                    timeout=15
                )
                end_time = time.time()
                result['response_time'] = round(end_time - start_time, 2)
                
                if response.status_code == 200:
                    result['status'] = "✅ 可用"
                    try:
                        response_data = response.json()
                        result['sample_response'] = str(response_data)[:100] + "..." if len(str(response_data)) > 100 else str(response_data)
                    except:
                        result['sample_response'] = "响应解析失败"
                else:
                    result['status'] = "❌ 不可用"
                    result['error'] = f"状态码: {response.status_code}, 错误: {response.text[:200]}"
            else:
                # 其他模型测试
                start_time = time.time()
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": module['model'],
                        "messages": [{"role": "user", "content": module['test_input']}],
                        "max_tokens": 50
                    },
                    timeout=15
                )
                end_time = time.time()
                result['response_time'] = round(end_time - start_time, 2)
                
                if response.status_code == 200:
                    result['status'] = "✅ 可用"
                    try:
                        response_data = response.json()
                        if 'choices' in response_data and len(response_data['choices']) > 0:
                            content = response_data['choices'][0]['message']['content']
                            result['sample_response'] = content[:100] + "..." if len(content) > 100 else content
                    except:
                        result['sample_response'] = "响应解析失败"
                else:
                    result['status'] = "❌ 不可用"
                    result['error'] = f"状态码: {response.status_code}, 错误: {response.text[:200]}"
                    
        except requests.exceptions.Timeout:
            result['status'] = "⏰ 超时"
            result['error'] = "请求超时"
        except requests.exceptions.ConnectionError:
            result['status'] = "🔌 连接错误"
            result['error'] = "网络连接失败"
        except Exception as e:
            result['status'] = "❌ 其他错误"
            result['error'] = str(e)
        
        results.append(result)
        print(f"   📊 状态: {result['status']}")
        if result['response_time']:
            print(f"   ⏱️ 响应时间: {result['response_time']}秒")
        if result['error']:
            print(f"   ❌ 错误: {result['error']}")
        if result.get('sample_response'):
            print(f"   📝 示例响应: {result['sample_response']}")
    
    return results

def generate_summary_report(results):
    """生成总结报告"""
    print("\n" + "=" * 80)
    print("📊 功能模块可用性总结报告")
    print("=" * 80)
    
    total_modules = len(results)
    available_modules = len([r for r in results if r['status'] == "✅ 可用"])
    unavailable_modules = len([r for r in results if r['status'] == "❌ 不可用"])
    timeout_modules = len([r for r in results if r['status'] == "⏰ 超时"])
    error_modules = len([r for r in results if r['status'] in ["🔌 连接错误", "❌ 其他错误"]])
    
    print(f"📈 总体统计:")
    print(f"   📋 总功能模块数: {total_modules}")
    print(f"   ✅ 可用模块数: {available_modules}")
    print(f"   ❌ 不可用模块数: {unavailable_modules}")
    print(f"   ⏰ 超时模块数: {timeout_modules}")
    print(f"   🔌 错误模块数: {error_modules}")
    print(f"   📊 可用率: {round(available_modules/total_modules*100, 1)}%")
    
    print(f"\n📋 详细状态:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['module_name']}")
        print(f"      🎯 模型: {result['model']}")
        print(f"      📊 状态: {result['status']}")
        if result['response_time']:
            print(f"      ⏱️ 响应时间: {result['response_time']}秒")
        print()
    
    # 按状态分组
    print(f"\n🔍 按状态分组:")
    
    available_list = [r for r in results if r['status'] == "✅ 可用"]
    if available_list:
        print(f"   ✅ 可用模块 ({len(available_list)}个):")
        for module in available_list:
            print(f"      - {module['module_name']} ({module['model']})")
    
    unavailable_list = [r for r in results if r['status'] == "❌ 不可用"]
    if unavailable_list:
        print(f"   ❌ 不可用模块 ({len(unavailable_list)}个):")
        for module in unavailable_list:
            print(f"      - {module['module_name']} ({module['model']}) - {module['error']}")
    
    timeout_list = [r for r in results if r['status'] == "⏰ 超时"]
    if timeout_list:
        print(f"   ⏰ 超时模块 ({len(timeout_list)}个):")
        for module in timeout_list:
            print(f"      - {module['module_name']} ({module['model']})")
    
    error_list = [r for r in results if r['status'] in ["🔌 连接错误", "❌ 其他错误"]]
    if error_list:
        print(f"   🔌 错误模块 ({len(error_list)}个):")
        for module in error_list:
            print(f"      - {module['module_name']} ({module['model']}) - {module['error']}")
    
    return {
        "total_modules": total_modules,
        "available_modules": available_modules,
        "unavailable_modules": unavailable_modules,
        "timeout_modules": timeout_modules,
        "error_modules": error_modules,
        "availability_rate": round(available_modules/total_modules*100, 1),
        "results": results
    }

if __name__ == "__main__":
    import time
    
    print("🚀 开始全面检查所有6个功能板块")
    print("=" * 80)
    
    # 检查所有功能模块
    results = check_all_functional_modules()
    
    # 生成总结报告
    summary = generate_summary_report(results)
    
    print("\n" + "=" * 80)
    print("🎉 全面检查完成")
    
    if summary['availability_rate'] >= 80:
        print(f"✅ 系统状态良好: {summary['availability_rate']}% 的功能模块可用")
    elif summary['availability_rate'] >= 50:
        print(f"⚠️ 系统部分功能正常: {summary['availability_rate']}% 的功能模块可用")
    else:
        print(f"❌ 系统状态不佳: {summary['availability_rate']}% 的功能模块可用")
    
    print("=" * 80)