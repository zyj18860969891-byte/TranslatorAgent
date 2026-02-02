#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenManus TranslatorAgent 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取 requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="openmanus-translator-agent",
    version="1.0.0",
    author="OpenManus Team",
    author_email="team@openmanus.com",
    description="OpenManus TranslatorAgent - 智能视频翻译系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/openmanus-translator-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "ipywidgets>=8.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "translator-agent=translator_agent.cli:main",
            "openmanus-extract=translator_agent.cli:extract_main",
            "openmanus-translate=translator_agent.cli:translate_main",
            "openmanus-analyze=translator_agent.cli:analyze_main",
        ],
    },
    include_package_data=True,
    package_data={
        "translator_agent": [
            "config/*.json",
            "models/*.json",
            "templates/*.html",
            "static/*",
        ],
    },
    zip_safe=False,
    keywords="video translation, subtitle extraction, emotion analysis, localization, ai, nlp, computer vision",
    project_urls={
        "Bug Reports": "https://github.com/your-org/openmanus-translator-agent/issues",
        "Source": "https://github.com/your-org/openmanus-translator-agent",
        "Documentation": "https://docs.openmanus.com",
    },
)