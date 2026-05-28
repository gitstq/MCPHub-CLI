#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCPHub-CLI 🚀
轻量级MCP Server智能发现、管理与配置引擎
Lightweight MCP Server Discovery, Management & Configuration Engine

Author: gitstq
License: MIT
Python: >=3.8
"""

import json
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib.request
import urllib.error

__version__ = "1.0.0"
__author__ = "gitstq"

# MCP Server Registry - 精选优质MCP Server
MCP_REGISTRY = {
    "github": {
        "name": "GitHub MCP Server",
        "description": "Official GitHub MCP Server for repository management",
        "url": "https://github.com/github/github-mcp-server",
        "command": "docker",
        "args": ["-i", "run", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        "category": "development",
        "stars": 23900
    },
    "playwright": {
        "name": "Playwright MCP",
        "description": "Browser automation via Playwright",
        "url": "https://github.com/microsoft/playwright-mcp",
        "command": "npx",
        "args": ["@anthropic-ai/playwright-mcp@latest"],
        "env": {},
        "category": "automation",
        "stars": 22400
    },
    "context7": {
        "name": "Context7",
        "description": "Real-time code documentation for LLMs",
        "url": "https://github.com/upstash/context7",
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp@latest"],
        "env": {},
        "category": "development",
        "stars": 35000
    },
    "mindsdb": {
        "name": "MindsDB",
        "description": "AI analysis and knowledge engine for RAG",
        "url": "https://github.com/mindsdb/mindsdb",
        "command": "python",
        "args": ["-m", "mindsdb.mcp"],
        "env": {},
        "category": "ai",
        "stars": 36500
    },
    "fetch": {
        "name": "Fetch MCP",
        "description": "Web content fetching and processing",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch",
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "env": {},
        "category": "utility",
        "stars": 15000
    },
    "filesystem": {
        "name": "Filesystem MCP",
        "description": "Secure file system access",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"],
        "env": {},
        "category": "utility",
        "stars": 18000
    },
    "postgres": {
        "name": "PostgreSQL MCP",
        "description": "PostgreSQL database integration",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "env": {},
        "category": "database",
        "stars": 12000
    },
    "sqlite": {
        "name": "SQLite MCP",
        "description": "SQLite database operations",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
        "command": "uvx",
        "args": ["mcp-server-sqlite"],
        "env": {},
        "category": "database",
        "stars": 11000
    },
    "git": {
        "name": "Git MCP",
        "description": "Git repository operations",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
        "command": "uvx",
        "args": ["mcp-server-git"],
        "env": {},
        "category": "development",
        "stars": 14000
    },
    "brave-search": {
        "name": "Brave Search MCP",
        "description": "Web search via Brave Search API",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": ""},
        "category": "search",
        "stars": 10000
    },
    "puppeteer": {
        "name": "Puppeteer MCP",
        "description": "Browser automation via Puppeteer",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {},
        "category": "automation",
        "stars": 13000
    },
    "slack": {
        "name": "Slack MCP",
        "description": "Slack workspace integration",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {"SLACK_BOT_TOKEN": "", "SLACK_TEAM_ID": ""},
        "category": "communication",
        "stars": 9000
    }
}


@dataclass
class MCPConfig:
    """MCP Server配置数据类"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str = ""
    enabled: bool = True


class MCPHub:
    """MCPHub核心类"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "mcphub"
        self.config_file = self.config_dir / "config.json"
        self.servers_file = self.config_dir / "servers.json"
        self.ensure_config_dir()

    def ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_claude_config_path(self) -> Optional[Path]:
        """获取Claude Desktop配置路径"""
        possible_paths = [
            Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",  # macOS
            Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",  # Windows
            Path.home() / ".config" / "Claude" / "claude_desktop_config.json",  # Linux
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return possible_paths[0]  # 返回默认路径

    def get_cline_config_path(self) -> Optional[Path]:
        """获取Cline配置路径"""
        possible_paths = [
            Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",  # macOS
            Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",  # Windows
            Path.home() / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",  # Linux
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return possible_paths[0]

    def load_config(self) -> Dict:
        """加载MCPHub配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"installed_servers": []}

    def save_config(self, config: Dict):
        """保存MCPHub配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def load_claude_config(self) -> Dict:
        """加载Claude Desktop配置"""
        path = self.get_claude_config_path()
        if path and path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"mcpServers": {}}

    def save_claude_config(self, config: Dict):
        """保存Claude Desktop配置"""
        path = self.get_claude_config_path()
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

    def load_cline_config(self) -> Dict:
        """加载Cline配置"""
        path = self.get_cline_config_path()
        if path and path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"mcpServers": {}}

    def save_cline_config(self, config: Dict):
        """保存Cline配置"""
        path = self.get_cline_config_path()
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

    def list_servers(self, category: Optional[str] = None) -> List[Dict]:
        """列出可用的MCP Server"""
        servers = []
        for key, server in MCP_REGISTRY.items():
            if category and server.get("category") != category:
                continue
            server_info = {
                "id": key,
                **server
            }
            servers.append(server_info)
        return sorted(servers, key=lambda x: x.get("stars", 0), reverse=True)

    def search_servers(self, query: str) -> List[Dict]:
        """搜索MCP Server"""
        results = []
        query_lower = query.lower()
        for key, server in MCP_REGISTRY.items():
            if (query_lower in key.lower() or
                query_lower in server.get("name", "").lower() or
                query_lower in server.get("description", "").lower() or
                query_lower in server.get("category", "").lower()):
                results.append({"id": key, **server})
        return sorted(results, key=lambda x: x.get("stars", 0), reverse=True)

    def install_server(self, server_id: str, target: str = "claude", env_vars: Optional[Dict] = None) -> bool:
        """安装MCP Server"""
        if server_id not in MCP_REGISTRY:
            print(f"❌ 未找到MCP Server: {server_id}")
            return False

        server = MCP_REGISTRY[server_id]
        config = self.load_config()

        # 准备环境变量
        env = server.get("env", {}).copy()
        if env_vars:
            env.update(env_vars)

        # 检查必需的环境变量
        for key, value in env.items():
            if not value:
                value = input(f"请输入 {key}: ").strip()
                env[key] = value

        server_config = {
            "command": server["command"],
            "args": server["args"].copy(),
            "env": env
        }

        # 添加到目标配置
        if target == "claude":
            claude_config = self.load_claude_config()
            claude_config.setdefault("mcpServers", {})[server_id] = server_config
            self.save_claude_config(claude_config)
        elif target == "cline":
            cline_config = self.load_cline_config()
            cline_config.setdefault("mcpServers", {})[server_id] = server_config
            self.save_cline_config(cline_config)
        else:
            print(f"❌ 不支持的目标: {target}")
            return False

        # 更新MCPHub配置
        if server_id not in config["installed_servers"]:
            config["installed_servers"].append(server_id)
            self.save_config(config)

        print(f"✅ 成功安装 {server['name']} 到 {target}")
        return True

    def uninstall_server(self, server_id: str, target: str = "all") -> bool:
        """卸载MCP Server"""
        config = self.load_config()

        if target in ("claude", "all"):
            claude_config = self.load_claude_config()
            if server_id in claude_config.get("mcpServers", {}):
                del claude_config["mcpServers"][server_id]
                self.save_claude_config(claude_config)
                print(f"✅ 已从Claude Desktop卸载 {server_id}")

        if target in ("cline", "all"):
            cline_config = self.load_cline_config()
            if server_id in cline_config.get("mcpServers", {}):
                del cline_config["mcpServers"][server_id]
                self.save_cline_config(cline_config)
                print(f"✅ 已从Cline卸载 {server_id}")

        if server_id in config["installed_servers"]:
            config["installed_servers"].remove(server_id)
            self.save_config(config)

        return True

    def list_installed(self) -> List[Dict]:
        """列出已安装的MCP Server"""
        config = self.load_config()
        claude_config = self.load_claude_config()
        cline_config = self.load_cline_config()

        installed = []
        for server_id in config.get("installed_servers", []):
            server_info = MCP_REGISTRY.get(server_id, {})
            status = {
                "id": server_id,
                "name": server_info.get("name", server_id),
                "in_claude": server_id in claude_config.get("mcpServers", {}),
                "in_cline": server_id in cline_config.get("mcpServers", {}),
                **server_info
            }
            installed.append(status)
        return installed

    def sync_to_cline(self):
        """同步Claude配置到Cline"""
        claude_config = self.load_claude_config()
        cline_config = self.load_cline_config()

        cline_config["mcpServers"] = claude_config.get("mcpServers", {}).copy()
        self.save_cline_config(cline_config)
        print("✅ 已同步Claude Desktop配置到Cline")

    def sync_to_claude(self):
        """同步Cline配置到Claude"""
        claude_config = self.load_claude_config()
        cline_config = self.load_cline_config()

        claude_config["mcpServers"] = cline_config.get("mcpServers", {}).copy()
        self.save_claude_config(claude_config)
        print("✅ 已同步Cline配置到Claude Desktop")

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for server in MCP_REGISTRY.values():
            categories.add(server.get("category", "other"))
        return sorted(list(categories))

    def export_config(self, output_path: str):
        """导出配置"""
        config = {
            "mcphub_version": __version__,
            "export_time": datetime.now().isoformat(),
            "installed_servers": self.load_config().get("installed_servers", []),
            "claude_config": self.load_claude_config(),
            "cline_config": self.load_cline_config()
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已导出到: {output_path}")

    def import_config(self, input_path: str):
        """导入配置"""
        with open(input_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "claude_config" in config:
            self.save_claude_config(config["claude_config"])
        if "cline_config" in config:
            self.save_cline_config(config["cline_config"])
        if "installed_servers" in config:
            self.save_config({"installed_servers": config["installed_servers"]})

        print(f"✅ 配置已从 {input_path} 导入")


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║  🚀 MCPHub-CLI v1.0.0                                      ║
║  轻量级MCP Server智能发现、管理与配置引擎                  ║
║  Lightweight MCP Server Discovery & Management Engine     ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_list(hub: MCPHub, args):
    """列出MCP Server命令"""
    servers = hub.list_servers(category=args.category)

    if args.category:
        print(f"\n📂 分类: {args.category}\n")
    else:
        print("\n📋 可用MCP Server列表\n")

    print(f"{'ID':<20} {'名称':<25} {'分类':<12} {'Stars':<8} 描述")
    print("-" * 100)

    for server in servers:
        server_id = server["id"]
        name = server.get("name", "")[:24]
        category = server.get("category", "other")
        stars = server.get("stars", 0)
        desc = server.get("description", "")[:40]
        print(f"{server_id:<20} {name:<25} {category:<12} {stars:<8} {desc}")

    print(f"\n共 {len(servers)} 个MCP Server")


def cmd_search(hub: MCPHub, args):
    """搜索MCP Server命令"""
    results = hub.search_servers(args.query)

    if not results:
        print(f"\n🔍 未找到与 '{args.query}' 相关的MCP Server")
        return

    print(f"\n🔍 搜索结果: '{args.query}'\n")
    print(f"{'ID':<20} {'名称':<25} {'分类':<12} {'Stars':<8} 描述")
    print("-" * 100)

    for server in results:
        server_id = server["id"]
        name = server.get("name", "")[:24]
        category = server.get("category", "other")
        stars = server.get("stars", 0)
        desc = server.get("description", "")[:40]
        print(f"{server_id:<20} {name:<25} {category:<12} {stars:<8} {desc}")

    print(f"\n共找到 {len(results)} 个结果")


def cmd_install(hub: MCPHub, args):
    """安装MCP Server命令"""
    env_vars = {}
    if args.env:
        for env in args.env:
            if '=' in env:
                key, value = env.split('=', 1)
                env_vars[key] = value

    hub.install_server(args.server_id, target=args.target, env_vars=env_vars)


def cmd_uninstall(hub: MCPHub, args):
    """卸载MCP Server命令"""
    hub.uninstall_server(args.server_id, target=args.target)


def cmd_installed(hub: MCPHub, args):
    """列出已安装的MCP Server命令"""
    installed = hub.list_installed()

    if not installed:
        print("\n📭 尚未安装任何MCP Server")
        print("使用 'mcphub list' 查看可用Server，使用 'mcphub install <id>' 安装")
        return

    print("\n📦 已安装的MCP Server\n")
    print(f"{'ID':<20} {'名称':<25} {'Claude':<8} {'Cline':<8} 描述")
    print("-" * 90)

    for server in installed:
        server_id = server["id"]
        name = server.get("name", "")[:24]
        in_claude = "✅" if server.get("in_claude") else "❌"
        in_cline = "✅" if server.get("in_cline") else "❌"
        desc = server.get("description", "")[:35]
        print(f"{server_id:<20} {name:<25} {in_claude:<8} {in_cline:<8} {desc}")

    print(f"\n共 {len(installed)} 个已安装Server")


def cmd_sync(hub: MCPHub, args):
    """同步配置命令"""
    if args.direction == "to-cline":
        hub.sync_to_cline()
    elif args.direction == "to-claude":
        hub.sync_to_claude()
    else:
        print("❌ 无效的同步方向，使用 'to-cline' 或 'to-claude'")


def cmd_categories(hub: MCPHub, args):
    """列出分类命令"""
    categories = hub.get_categories()

    print("\n📂 MCP Server分类\n")
    for cat in categories:
        count = sum(1 for s in MCP_REGISTRY.values() if s.get("category") == cat)
        print(f"  • {cat:<15} ({count}个Server)")


def cmd_export(hub: MCPHub, args):
    """导出配置命令"""
    hub.export_config(args.output)


def cmd_import(hub: MCPHub, args):
    """导入配置命令"""
    hub.import_config(args.input)


def cmd_info(hub: MCPHub, args):
    """显示MCP Server详情命令"""
    if args.server_id not in MCP_REGISTRY:
        print(f"❌ 未找到MCP Server: {args.server_id}")
        return

    server = MCP_REGISTRY[args.server_id]
    print(f"\n📋 {server.get('name', args.server_id)}\n")
    print(f"  ID:          {args.server_id}")
    print(f"  名称:        {server.get('name', 'N/A')}")
    print(f"  描述:        {server.get('description', 'N/A')}")
    print(f"  分类:        {server.get('category', 'other')}")
    print(f"  Stars:       {server.get('stars', 0)}")
    print(f"  项目地址:    {server.get('url', 'N/A')}")
    print(f"\n  命令:        {server.get('command', 'N/A')}")
    print(f"  参数:        {' '.join(server.get('args', []))}")

    env = server.get("env", {})
    if env:
        print(f"\n  环境变量:")
        for key in env.keys():
            print(f"    • {key}")


def cmd_init(hub: MCPHub, args):
    """初始化配置命令"""
    print("\n🔧 初始化MCPHub配置...")

    # 创建配置目录
    hub.ensure_config_dir()

    # 初始化配置文件
    config = hub.load_config()
    if not config.get("installed_servers"):
        config["installed_servers"] = []
        hub.save_config(config)

    print(f"✅ 配置目录已创建: {hub.config_dir}")
    print(f"✅ 配置文件位置: {hub.config_file}")

    # 显示Claude配置路径
    claude_path = hub.get_claude_config_path()
    print(f"📁 Claude Desktop配置: {claude_path}")

    # 显示Cline配置路径
    cline_path = hub.get_cline_config_path()
    print(f"📁 Cline配置: {cline_path}")

    print("\n🎉 初始化完成！使用 'mcphub list' 查看可用Server")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog='mcphub',
        description='MCPHub-CLI: 轻量级MCP Server智能发现、管理与配置引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mcphub list                          # 列出所有可用MCP Server
  mcphub list --category development   # 按分类筛选
  mcphub search github                 # 搜索MCP Server
  mcphub install github                # 安装MCP Server到Claude
  mcphub install github --target cline # 安装到Cline
  mcphub installed                     # 查看已安装的Server
  mcphub uninstall github              # 卸载MCP Server
  mcphub sync to-cline                 # 同步Claude配置到Cline
  mcphub categories                    # 查看所有分类
  mcphub info github                   # 查看Server详情
  mcphub export backup.json            # 导出配置
  mcphub import backup.json            # 导入配置
        """
    )

    parser.add_argument('--version', '-v', action='version', version=f'MCPHub-CLI v{__version__}')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # list命令
    list_parser = subparsers.add_parser('list', help='列出可用MCP Server')
    list_parser.add_argument('--category', '-c', help='按分类筛选')
    list_parser.set_defaults(func=cmd_list)

    # search命令
    search_parser = subparsers.add_parser('search', help='搜索MCP Server')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.set_defaults(func=cmd_search)

    # install命令
    install_parser = subparsers.add_parser('install', help='安装MCP Server')
    install_parser.add_argument('server_id', help='MCP Server ID')
    install_parser.add_argument('--target', '-t', choices=['claude', 'cline'], default='claude',
                                help='安装目标 (默认: claude)')
    install_parser.add_argument('--env', '-e', action='append', help='设置环境变量 (KEY=value)')
    install_parser.set_defaults(func=cmd_install)

    # uninstall命令
    uninstall_parser = subparsers.add_parser('uninstall', help='卸载MCP Server')
    uninstall_parser.add_argument('server_id', help='MCP Server ID')
    uninstall_parser.add_argument('--target', '-t', choices=['claude', 'cline', 'all'], default='all',
                                  help='卸载目标 (默认: all)')
    uninstall_parser.set_defaults(func=cmd_uninstall)

    # installed命令
    installed_parser = subparsers.add_parser('installed', help='列出已安装的MCP Server')
    installed_parser.set_defaults(func=cmd_installed)

    # sync命令
    sync_parser = subparsers.add_parser('sync', help='同步配置')
    sync_parser.add_argument('direction', choices=['to-cline', 'to-claude'], help='同步方向')
    sync_parser.set_defaults(func=cmd_sync)

    # categories命令
    categories_parser = subparsers.add_parser('categories', help='列出分类')
    categories_parser.set_defaults(func=cmd_categories)

    # export命令
    export_parser = subparsers.add_parser('export', help='导出配置')
    export_parser.add_argument('output', help='输出文件路径')
    export_parser.set_defaults(func=cmd_export)

    # import命令
    import_parser = subparsers.add_parser('import', help='导入配置')
    import_parser.add_argument('input', help='输入文件路径')
    import_parser.set_defaults(func=cmd_import)

    # info命令
    info_parser = subparsers.add_parser('info', help='显示MCP Server详情')
    info_parser.add_argument('server_id', help='MCP Server ID')
    info_parser.set_defaults(func=cmd_info)

    # init命令
    init_parser = subparsers.add_parser('init', help='初始化配置')
    init_parser.set_defaults(func=cmd_init)

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    hub = MCPHub()
    args.func(hub, args)


if __name__ == '__main__':
    main()
