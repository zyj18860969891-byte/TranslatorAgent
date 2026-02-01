#!/usr/bin/env python3
"""测试运行器"""

import sys
import pytest

def main():
    """运行所有测试"""
    sys.exit(pytest.main(["-v", "--tb=short", "tests/"]))

if __name__ == "__main__":
    main()