"""
Zaifer MCP アカウント情報ツール

Zaif APIのアカウント情報関連機能をMCPツールとして公開する実装
"""
from mcp.server.fastmcp import FastMCP
from zaifer_mcp.api.client import ZaifApi
from zaifer_mcp.models import AccountBalance


def register_account_tools(mcp: FastMCP, api: ZaifApi):
    """
    Zaifのアカウント情報APIをMCPツールとして登録する
    
    Args:
        mcp: FastMCPインスタンス
        api: ZaifApiインスタンス
    """
    @mcp.tool()
    def get_account_balance() -> AccountBalance:
        """
        アカウントの残高情報を取得します。
        
        このツールは、取引前の残高確認や投資可能額の算出に使用します。
        すべての通貨の残高を一度に取得し、利用可能な資金を確認できます。
        
        使用例:
        - 取引前に利用可能な資金を確認したい場合
        - ポートフォリオの総資産価値を計算したい場合
        - 各通貨の保有量を確認したい場合
        - 投資可能額を把握したい場合
        
        注意: このツールを使用するには、環境変数にAPIキーとシークレットが設定されている必要があります。
        
        Returns:
            AccountBalance: アカウント残高情報
                - balances: 各通貨の残高情報（通貨コードをキーとする辞書）
                - permissions: 利用権限情報（APIの各機能に対する権限を示す辞書）
        
        Raises:
            ValueError: 認証情報が設定されていない場合や、APIエラーが発生した場合
        """
        if not api.account.http.auth_provider:
            raise ValueError("認証情報が設定されていません。APIキーとシークレットを.envファイルに設定してください。")
        
        # 全通貨の残高を取得
        return api.account.get_info()
