#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCPHub-CLI 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="mcphub-cli",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="轻量级MCP Server智能发现、管理与配置引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/MCPHub-CLI",
    py_modules=["mcphub"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mcphub=mcphub:main",
        ],
    },
    keywords="mcp, model-context-protocol, ai, claude, cli, server-management",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/MCPHub-CLI/issues",
        "Source": "https://github.com/gitstq/MCPHub-CLI",
    },
)
