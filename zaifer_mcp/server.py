#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zaifer MCP Server

Zaif暗号資産取引所のAPIをModel Context Protocol (MCP)経由で直接利用可能にするサーバー
"""

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from zaifer_mcp.api.client import ZaifApi


def load_environment(env_file: str = '.env') -> None:
    """環境変数を読み込む"""
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        print(f"警告: 環境変数ファイル '{env_file}' が見つかりません。")


def create_zaif_api() -> ZaifApi:
    """Zaif APIクライアントを作成"""
    api_key = os.getenv("ZAIF_API_KEY")
    api_secret = os.getenv("ZAIF_API_SECRET")
    return ZaifApi(api_key=api_key, api_secret=api_secret)


def register_all_components(mcp: FastMCP, zaif_api: ZaifApi) -> None:
    """全てのツール・リソース・プロンプトを登録"""
    # ツールの登録
    from zaifer_mcp.tools.market import register_market_tools
    from zaifer_mcp.tools.account import register_account_tools
    from zaifer_mcp.tools.trade import register_trade_tools
    from zaifer_mcp.tools.chart import register_chart_tools
    
    register_market_tools(mcp, zaif_api)
    register_account_tools(mcp, zaif_api)
    register_trade_tools(mcp, zaif_api)
    register_chart_tools(mcp, zaif_api)
    
    # リソースの登録
    # (現在リソースは実装されていません)
    
    # プロンプトの登録
    # (現在プロンプトは実装されていません))


def create_server_config(transport: str, port: int = 8000, host: str = "0.0.0.0", debug: bool = False) -> dict:
    """トランスポートに応じたサーバー設定を生成"""
    config = {
        'debug': debug,
        'log_level': 'DEBUG' if debug else 'INFO'
    }
    
    if transport == 'streamable-http':
        config.update({
            'port': port,
            'host': host
        })
    
    return config


def create_mcp_server(zaif_api: ZaifApi, **server_config) -> FastMCP:
    """MCPサーバーインスタンスを作成"""
    mcp = FastMCP("ZaiferAPI", **server_config)
    register_all_components(mcp, zaif_api)
    return mcp


def run_server(debug=False, transport='stdio', port=8000, host="0.0.0.0", env_file='.env'):
    """
    MCPサーバーを実行する
    
    Args:
        debug: デバッグモードで実行するかどうか
        transport: 使用するトランスポート ('stdio', 'streamable-http')
        port: HTTPトランスポート使用時のポート番号
        host: HTTPトランスポート使用時のホスト
        env_file: 環境変数ファイルのパス
    
    Returns:
        終了コード
    """
    # 1. 環境設定
    load_environment(env_file)
    
    # 2. API初期化
    zaif_api = create_zaif_api()
    
    # 3. サーバー設定生成
    server_config = create_server_config(transport, port, host, debug)
    
    # 4. 起動ログ
    if debug:
        print("デバッグモードで実行します")
    
    print(f"zaifer-mcp サーバーを起動しています...")
    print(f"サーバー名: ZaiferAPI")
    print(f"トランスポート: {transport}")
    
    if transport == 'streamable-http':
        print(f"ホスト: {host}")
        print(f"ポート: {port}")
    
    # 5. サーバー作成・実行
    try:
        mcp = create_mcp_server(zaif_api, **server_config)
        mcp.run(transport=transport)
        return 0
    except ValueError as e:
        if "Unknown transport" in str(e):
            print(f"エラー: 不明なトランスポート '{transport}'")
            print("対応トランスポート: stdio, streamable-http")
        else:
            print(f"エラー: {str(e)}")
        return 1
    except Exception as e:
        print(f"エラー: サーバーの起動に失敗しました - {str(e)}")
        return 1


if __name__ == "__main__":
    run_server()
