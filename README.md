# zaifer-mcp

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)

Zaif暗号資産取引所のAPIを[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)経由で利用可能にするPythonライブラリです。ClaudeなどのLLMアシスタントから自然言語でZaif APIの機能を直接呼び出せます。

## ⚠️ 重要な注意事項

**本アプリケーションは非公式・非公認のサードパーティ製ツールです。**
Zaif取引所および株式会社Zaifとは一切関係がありません。

## 特徴

- 🤖 **LLMフレンドリー**: Claude、ChatGPTなどのLLMから自然言語で暗号資産取引機能を利用
- 🔒 **セキュア**: API認証が必要な操作は適切に保護され、公開情報は安全にアクセス可能
- 📊 **包括的な機能**: 市場情報、チャートデータ、取引、アカウント管理の全機能をサポート  
- 🚀 **高速**: FastMCPフレームワークによる効率的な実装
- 🔌 **柔軟な接続**: STDIO（ローカル）とHTTP（リモート）の両方の通信方式をサポート

## サポート通貨ペア

- **BTC/JPY** (ビットコイン/日本円)
- **ETH/JPY** (イーサリアム/日本円)  
- **XYM/JPY** (シンボル/日本円)

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/curio184/zaifer-mcp.git
cd zaifer-mcp

# パッケージをインストール
pip install -e .
```

## 環境設定

zaifer-mcpは**APIキーなしでも市場情報の取得が可能**です。Zaifの口座をお持ちでAPIキーを発行いただければ、残高確認や取引機能を含むすべての機能をご利用いただけます。

## 使用方法

### Claude Desktopとの連携

```bash
# リポジトリをクローン
git clone https://github.com/curio184/zaifer-mcp.git
```

Claude Desktop（デスクトップ版）のMCP設定ファイル `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) または `%APPDATA%\Claude\claude_desktop_config.json` (Windows) に以下を設定：

```json
{
  "mcpServers": {
    "zaifer-mcp": {
      "command": "python",
      "args": ["/path/to/zaifer-mcp/zaifer_mcp/__main__.py"],
      "env": {
        "ZAIF_API_KEY": "your_api_key_here",
        "ZAIF_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

APIキーなしで市場情報のみ利用する場合は、`env`セクションを省略できます。設定後、Claude Desktopを再起動すると、zaifer-mcpの機能が利用可能になります。

## 使用例

### Claude での基本的な使用例

```
ユーザー: ビットコインの現在価格を教えてください

Claude: 現在のビットコイン（BTC/JPY）の価格情報をお調べします。

【BTC/JPY 価格情報】
- 現在価格: ¥14,500,000
- 24時間変動: +2.3%
- 高値: ¥14,520,000 / 安値: ¥14,380,000
- 出来高: 150.3 BTC
```

Claude は `get_ticker` ツールを自動的に呼び出し、リアルタイムの市場データを取得して回答します。

## 開発者向け情報

開発環境のセットアップ、デバッグ方法、アーキテクチャの詳細については[DEVELOPMENT.md](DEVELOPMENT.md)をご覧ください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 著者

**Yusuke Oya** - [curio@antique-cafe.net](mailto:curio@antique-cafe.net)

## 関連リンク

- [Zaif API公式ドキュメント](https://zaif-api-document.readthedocs.io/ja/latest/)
- [Zaif公式サイト](https://zaif.jp/)
- [Model Context Protocol公式サイト](https://modelcontextprotocol.io/)
- [FastMCP公式ドキュメント](https://github.com/jlowin/fastmcp)

## 免責事項

本ソフトウェアは暗号資産取引所のAPIを利用しますが、取引の結果について一切の責任を負いません。
本アプリケーションはZaif取引所の非公式・非公認のサードパーティ製ツールであり、Zaif取引所および株式会社Zaifによる保証はありません。
実際の取引を行う前に、必ず動作を十分に確認し、自己責任で利用してください。
