"""
CLI 主入口

提供命令行工具的主入口点
"""

import sys
from click.testing import CliRunner
from .commands import cli


def main():
    """CLI 主入口函数"""
    # 直接调用CLI，避免使用CliRunner
    cli()


if __name__ == '__main__':
    main()