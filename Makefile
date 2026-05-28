# MCPHub-CLI Makefile
.PHONY: help install install-dev uninstall test clean build lint format

PYTHON := python3
PIP := pip3

help:
	@echo "MCPHub-CLI 构建脚本"
	@echo ""
	@echo "可用目标:"
	@echo "  install      - 安装到系统"
	@echo "  install-dev  - 开发模式安装"
	@echo "  uninstall    - 卸载"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  build        - 构建分发包"
	@echo "  clean        - 清理构建文件"

install:
	$(PIP) install . --break-system-packages

install-dev:
	$(PIP) install -e . --break-system-packages

uninstall:
	$(PIP) uninstall mcphub-cli -y

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m flake8 mcphub.py --max-line-length=120
	$(PYTHON) -m pylint mcphub.py --disable=C,R

format:
	$(PYTHON) -m black mcphub.py --line-length=120

build:
	$(PYTHON) -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
