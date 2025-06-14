#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
zaifer_mcp コマンドラインエントリーポイント
"""

import sys
import argparse
from zaifer_mcp.server import run_server


def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(description='Zaifer MCP Server')
    parser.add_argument('--version', action='store_true', help='バージョン情報を表示')
    parser.add_argument('--debug', action='store_true', help='デバッグモードで実行')
    parser.add_argument('--transport', default='stdio', choices=['stdio', 'streamable-http'],
                        help='使用するトランスポート (デフォルト: stdio)')
    parser.add_argument('--port', type=int, default=8000,
                        help='HTTPトランスポート使用時のポート番号 (デフォルト: 8000)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='HTTPトランスポート使用時のホスト (デフォルト: 0.0.0.0)')
    parser.add_argument('--env-file', default='.env',
                        help='環境変数ファイルのパス (デフォルト: .env)')

    args = parser.parse_args()

    if args.version:
        from zaifer_mcp import __version__
        print(f"zaifer-mcp version {__version__}")
        return 0

    return run_server(
        debug=args.debug,
        transport=args.transport,
        port=args.port,
        host=args.host,
        env_file=args.env_file
    )


if __name__ == "__main__":
    sys.exit(main())
