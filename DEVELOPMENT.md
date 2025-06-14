# zaifer-mcp 開発ガイド

このドキュメントは、zaifer-mcpの開発に関する詳細情報を提供します。

## 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/curio184/zaifer-mcp.git
cd zaifer-mcp

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用パッケージのインストール
pip install -e ".[dev]"

# 開発・テスト用の環境変数設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## デバッグ

推奨デバッグ環境：**VS Code + MCP Inspector + HTTPモード**

### 1. VS Code設定

`.vscode/launch.json`を作成：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Zaifer MCP Server (HTTP)",
            "type": "debugpy",
            "request": "launch",
            "module": "zaifer_mcp",
            "args": [
                "--transport", "streamable-http",
                "--port", "8080",
                "--host", "127.0.0.1",
                "--debug"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### 2. デバッグ手順

```bash
# 1. VS CodeでF5キーを押してデバッグサーバー起動

# 2. 別ターミナルでMCP Inspector起動
npx @modelcontextprotocol/inspector

# 3. ブラウザで http://127.0.0.1:6274 を開く
# 4. Inspector設定:
#    - Transport: HTTP/Streamable HTTP  
#    - URL: http://127.0.0.1:8080/mcp
```

VS Codeでブレークポイントを設定し、Inspector からツールを実行してデバッグできます。

## アーキテクチャ

### プロジェクト構造

```
zaifer_mcp/
├── api/              # Zaif API クライアント実装
│   └── client.py     # HTTPクライアント、認証、API呼び出し
├── models/           # データモデル定義（@dataclass）
│   ├── account.py    # アカウント関連モデル
│   ├── market.py     # 市場情報モデル
│   ├── trade.py      # 取引関連モデル
│   └── chart.py      # チャートデータモデル
├── tools/            # MCP Tools実装
│   ├── account.py    # アカウント情報ツール
│   ├── market.py     # 市場情報ツール
│   ├── trade.py      # 取引ツール
│   └── chart.py      # チャートツール
├── prompts/          # MCP Prompts実装
│   └── market.py     # 市場分析プロンプト
└── server.py         # MCPサーバーエントリーポイント
```

### 設計思想

- **Tools vs Resources**: 認証が必要な操作や動的なデータはTools、静的な公開情報はResourcesとして実装
- **型安全性**: すべてのAPI応答をPydantic/dataclassモデルで型安全に定義
- **LLMフレンドリー**: 関数名、引数名、戻り値構造をLLMが理解しやすい形で設計
