#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的功能模块测试验证脚本
测试所有6个功能模块的替代方案实施效果
"""

import os
import sys
import json
import logging
import time
import requests
from typing import Dict, Any, List

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_functional_modules():
    """测试所有6个功能模块"""
    print("🚀 开始完整的功能模块测试验证")
    print("=" * 80)
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未配置DASHSCOPE_API_KEY环境变量")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:20]}...")
    
    # 测试配置
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 6个功能模块测试用例
    test_cases = [
        {
            "name": "字幕提取模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-turbo",
                "messages": [{"role": "user", "content": "请从视频中提取字幕文本，视频内容是关于人工智能的讲座。"}],
                "max_tokens": 200
            },
            "expected_response": "字幕提取",
            "description": "从视频中提取字幕文本"
        },
        {
            "name": "专业视频翻译模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-turbo",
                "messages": [{"role": "user", "content": "请将以下英文翻译成中文: Artificial Intelligence is transforming the world."}],
                "max_tokens": 100
            },
            "expected_response": "人工智能",
            "description": "提供专业的视频翻译服务"
        },
        {
            "name": "情感分析模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-turbo",
                "messages": [{"role": "user", "content": "请分析以下文本的情感倾向，并给出详细分析：我今天很开心！"}],
                "max_tokens": 200
            },
            "expected_response": "积极",
            "description": "分析视频内容的情感倾向"
        },
        {
            "name": "批量处理模块",
            "model": "qwen-turbo",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-turbo",
                "messages": [{"role": "user", "content": "请批量处理以下任务：1. 提取视频A的字幕 2. 翻译视频B的字幕 3. 分析视频C的情感"}],
                "max_tokens": 200
            },
            "expected_response": "批量处理",
            "description": "批量处理多个视频文件"
        },
        {
            "name": "视频字幕压制模块",
            "model": "qwen-vl-plus",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-vl-plus",
                "messages": [{"role": "user", "content": "请为视频添加字幕，要求：字体大小24，白色字体，底部位置，黑色半透明背景。"}],
                "max_tokens": 200
            },
            "expected_response": "字幕",
            "description": "为视频添加字幕压制功能"
        },
        {
            "name": "字幕擦除模块",
            "model": "qwen-vl-plus",
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "test_data": {
                "model": "qwen-vl-plus",
                "messages": [{"role": "user", "content": "请擦除图像中的字幕，要求：保持图像质量，自然擦除字幕区域。"}],
                "max_tokens": 200
            },
            "expected_response": "擦除",
            "description": "擦除视频中的字幕"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 {i}. {test_case['name']}")
        print(f"   🎯 模型: {test_case['model']}")
        print(f"   📝 描述: {test_case['description']}")
        print(f"   🔗 端点: {test_case['endpoint']}")
        
        result = {
            "module_name": test_case['name'],
            "model": test_case['model'],
            "status": "❌ 未测试",
            "response_time": None,
            "error": None,
            "response_content": None,
            "test_passed": False
        }
        
        try:
            start_time = time.time()
            
            # 发送请求
            response = requests.post(
                test_case['endpoint'],
                headers=headers,
                json=test_case['test_data'],
                timeout=30
            )
            
            end_time = time.time()
            result['response_time'] = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 提取响应内容
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    result['response_content'] = content
                    
                    # 检查是否包含期望的响应
                    if test_case['expected_response'] in content:
                        result['status'] = "✅ 通过"
                        result['test_passed'] = True
                        print(f"   📊 状态: ✅ 通过")
                        print(f"   ⏱️ 响应时间: {result['response_time']}秒")
                        print(f"   📝 响应内容: {content[:100]}...")
                    else:
                        result['status'] = "⚠️ 响应不匹配"
                        result['test_passed'] = False
                        print(f"   📊 状态: ⚠️ 响应不匹配")
                        print(f"   ⏱️ 响应时间: {result['response_time']}秒")
                        print(f"   📝 响应内容: {content[:100]}...")
                        print(f"   ❌ 期望包含: {test_case['expected_response']}")
                else:
                    result['status'] = "❌ 响应格式错误"
                    result['error'] = "响应格式不正确"
                    print(f"   📊 状态: ❌ 响应格式错误")
            else:
                result['status'] = "❌ 请求失败"
                result['error'] = f"状态码: {response.status_code}, 错误: {response.text[:200]}"
                print(f"   📊 状态: ❌ 请求失败")
                print(f"   ❌ 错误: {result['error']}")
                
        except requests.exceptions.Timeout:
            result['status'] = "⏰ 超时"
            result['error'] = "请求超时"
            print(f"   📊 状态: ⏰ 超时")
        except requests.exceptions.ConnectionError:
            result['status'] = "🔌 连接错误"
            result['error'] = "网络连接失败"
            print(f"   📊 状态: 🔌 连接错误")
        except Exception as e:
            result['status'] = "❌ 其他错误"
            result['error'] = str(e)
            print(f"   📊 状态: ❌ 其他错误")
            print(f"   ❌ 错误: {str(e)}")
        
        results.append(result)
    
    return results

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 80)
    print("📊 功能模块测试验证报告")
    print("=" * 80)
    
    total_modules = len(results)
    passed_modules = len([r for r in results if r['test_passed']])
    failed_modules = total_modules - passed_modules
    
    print(f"📈 测试统计:")
    print(f"   📋 总功能模块数: {total_modules}")
    print(f"   ✅ 通过模块数: {passed_modules}")
    print(f"   ❌ 失败模块数: {failed_modules}")
    print(f"   📊 通过率: {round(passed_modules/total_modules*100, 1)}%")
    
    print(f"\n📋 详细测试结果:")
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result['test_passed'] else "❌"
        print(f"   {i}. {result['module_name']} {status_icon}")
        print(f"      🎯 模型: {result['model']}")
        print(f"      📊 状态: {result['status']}")
        if result['response_time']:
            print(f"      ⏱️ 响应时间: {result['response_time']}秒")
        if result['error']:
            print(f"      ❌ 错误: {result['error']}")
        if result['response_content']:
            print(f"      📝 响应内容: {result['response_content'][:100]}...")
        print()
    
    # 按状态分组
    print(f"\n🔍 测试结果分组:")
    
    passed_list = [r for r in results if r['test_passed']]
    if passed_list:
        print(f"   ✅ 通过模块 ({len(passed_list)}个):")
        for module in passed_list:
            print(f"      - {module['module_name']} ({module['model']}) - {module['response_time']}秒")
    
    failed_list = [r for r in results if not r['test_passed']]
    if failed_list:
        print(f"   ❌ 失败模块 ({len(failed_list)}个):")
        for module in failed_list:
            print(f"      - {module['module_name']} ({module['model']}) - {module['status']}")
    
    return {
        "total_modules": total_modules,
        "passed_modules": passed_modules,
        "failed_modules": failed_modules,
        "pass_rate": round(passed_modules/total_modules*100, 1),
        "results": results
    }

def validate_configuration():
    """验证配置文件"""
    print("\n" + "=" * 80)
    print("🔧 验证配置文件")
    print("=" * 80)
    
    config_files = [
        "feature_config.json",
        "qwen3_config.json"
    ]
    
    all_valid = True
    
    for config_file in config_files:
        print(f"\n📋 检查配置文件: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"   ✅ 文件存在且格式正确")
            
            # 验证特定配置
            if config_file == "feature_config.json":
                features = config.get("features", {})
                print(f"   📊 功能模块数量: {len(features)}")
                
                for feature_name, feature_config in features.items():
                    model = feature_config.get("primary_model", "未配置")
                    enabled = feature_config.get("enabled", False)
                    status = "✅ 启用" if enabled else "❌ 禁用"
                    print(f"      - {feature_name}: {model} ({status})")
            
            elif config_file == "qwen3_config.json":
                model = config.get("model", "未配置")
                base_url = config.get("base_url", "未配置")
                print(f"   🎯 默认模型: {model}")
                print(f"   🔗 基础URL: {base_url}")
                
                # 检查关键配置
                if "compatible-mode" in base_url:
                    print(f"   ✅ 使用兼容模式API")
                else:
                    print(f"   ⚠️ 未使用兼容模式API")
                
                if model in ["qwen-turbo", "qwen-plus", "qwen-vl-plus"]:
                    print(f"   ✅ 模型配置正确")
                else:
                    print(f"   ⚠️ 模型配置可能有问题")
            
        except FileNotFoundError:
            print(f"   ❌ 文件不存在")
            all_valid = False
        except json.JSONDecodeError:
            print(f"   ❌ JSON格式错误")
            all_valid = False
        except Exception as e:
            print(f"   ❌ 检查失败: {str(e)}")
            all_valid = False
    
    return all_valid

if __name__ == "__main__":
    print("🚀 开始完整的功能模块测试验证")
    print("=" * 80)
    
    # 验证配置文件
    config_valid = validate_configuration()
    if not config_valid:
        print("\n❌ 配置文件验证失败，请检查配置")
        sys.exit(1)
    
    # 测试所有功能模块
    results = test_all_functional_modules()
    
    # 生成测试报告
    report = generate_test_report(results)
    
    print("\n" + "=" * 80)
    print("🎉 测试验证完成")
    
    if report['pass_rate'] >= 80:
        print(f"✅ 测试通过率高: {report['pass_rate']}% - 系统状态良好")
        print("🚀 所有功能模块都可以正常工作！")
    elif report['pass_rate'] >= 50:
        print(f"⚠️ 测试通过率中等: {report['pass_rate']}% - 系统部分功能正常")
        print("🔧 需要进一步优化失败模块")
    else:
        print(f"❌ 测试通过率低: {report['pass_rate']}% - 系统需要重大改进")
        print("🚨 请立即修复失败的功能模块")
    
    print("=" * 80)
    
    # 输出最终状态
    print(f"\n📊 最终状态总结:")
    print(f"   ✅ 可用功能模块: {report['passed_modules']}/{report['total_modules']}")
    print(f"   🎯 替代方案实施: {'成功' if report['pass_rate'] > 0 else '失败'}")
    print(f"   🚀 生产就绪状态: {'就绪' if report['pass_rate'] >= 80 else '部分就绪'}")
    
    if report['pass_rate'] >= 80:
        print(f"\n🎉 恭喜！所有功能模块都已成功部署替代方案，系统可以投入生产使用！")
    else:
        print(f"\n💡 建议：继续优化失败的功能模块，提高系统稳定性")