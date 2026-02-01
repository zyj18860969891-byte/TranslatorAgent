"""
测试运行脚本

运行所有单元测试和集成测试
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行 Translator Agent 测试...")
    
    # 获取测试目录
    test_dir = Path(__file__).parent
    
    # 运行所有测试
    exit_code = pytest.main([
        str(test_dir),
        "-v",  # 详细输出
        "--tb=short",  # 短格式的回溯信息
        "--cov=translator_agent",  # 代码覆盖率
        "--cov-report=html",  # 生成覆盖率报告
        "--cov-report=term-missing",  # 显示缺失覆盖率的行
        "--junit-xml=test_results.xml"  # JUnit XML 报告
    ])
    
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 测试失败！")
    
    return exit_code

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)