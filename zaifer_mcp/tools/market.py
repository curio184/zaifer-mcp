"""
Zaifer MCP 市場情報ツール

Zaif APIの市場情報関連機能をMCPツールとして公開する実装
"""

from mcp.server.fastmcp import FastMCP
from zaifer_mcp.api.client import ZaifApi
from zaifer_mcp.models import Ticker, OrderBook, CurrencyPair, SupportedPair


def register_market_tools(mcp: FastMCP, api: ZaifApi):
    """
    Zaifの市場情報APIをMCPツールとして登録する

    Args:
        mcp: FastMCPインスタンス
        api: ZaifApiインスタンス
    """

    @mcp.tool()
    def get_ticker(currency_pair: SupportedPair) -> Ticker:
        """
        指定した通貨ペアのティッカー情報を取得します。

        現在の市場価格統計を提供し、以下の用途で使用します：
        - 現在の市場価格と24時間の価格変動を確認したい場合
        - 売買注文の価格設定の参考にしたい場合
        - 市場の活発さ（取引量）を把握したい場合

        使用例:
        - ビットコインの現在価格を確認したい場合
        - 最適な注文価格を決定するため最良売買価格を確認したい場合
        - 24時間の価格レンジを分析したい場合

        Args:
            currency_pair: 通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）

        Returns:
            Ticker: ティッカー情報
                - last_price: 最終取引価格
                - high_price: 24時間最高値
                - low_price: 24時間最安値
                - ask_price: 最良売り価格
                - bid_price: 最良買い価格
                - volume: 24時間取引量

        Raises:
            ValueError: 通貨ペアが無効な場合や、APIエラーが発生した場合
        """
        return api.market.get_ticker(currency_pair)

    @mcp.tool()
    def get_market_depth(currency_pair: SupportedPair) -> OrderBook:
        """
        指定した通貨ペアの板情報を取得します。

        市場全体の売買注文状況を表示し、あなた個人の注文一覧（get_open_orders）とは異なります。
        全市場参加者の注文が価格順に並んだ情報で、以下の用途で使用します：
        - 市場の流動性と売買圧力を分析したい場合
        - 大量注文前に市場の深さを確認したい場合
        - サポート・レジスタンスレベルを特定したい場合

        使用例:
        - 大きな注文を出す前に市場の流動性を確認したい場合
        - 現在のビッド・アスクスプレッドを詳細に分析したい場合
        - 特定価格帯での注文量を確認したい場合

        Args:
            currency_pair: 通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）

        Returns:
            OrderBook: 市場全体の板情報
                - asks: 売り注文一覧（price・quantity）
                - bids: 買い注文一覧（price・quantity）

        Raises:
            ValueError: 通貨ペアが無効な場合や、APIエラーが発生した場合
        """
        return api.market.get_depth(currency_pair)

    @mcp.tool()
    def get_currency_pairs() -> list[CurrencyPair]:
        """
        対応している通貨ペア情報を取得します。

        取引可能な通貨ペアの詳細な制約情報を提供し、以下の用途で使用します：
        - 注文前に最小数量・価格制約を確認したい場合
        - 有効な注文パラメータを計算したい場合
        - 通貨ペアの取引ルールを理解したい場合

        使用例:
        - ビットコインの最小注文数量を確認したい場合
        - 価格の刻み幅に合わせて注文価格を調整したい場合
        - 通貨ペアごとの制約の違いを比較したい場合

        Returns:
            list[CurrencyPair]: 通貨ペア情報のリスト
                - currency_pair: 通貨ペア識別子（例: 'btc_jpy'）
                - min_quantity: 最小注文数量
                - quantity_step: 注文数量の刻み幅
                - min_price: 最小注文価格
                - price_step: 注文価格の刻み幅
                - price_precision: 価格表示の小数点桁数
                - display_name: 表示用名称（例: 'ビットコイン/円'）

        Raises:
            ValueError: APIエラーが発生した場合
        """
        all_pairs = api.market.get_currency_pairs("all")
        # 対応している通貨ペアのみをフィルタリング
        supported_pairs = [
            p for p in all_pairs if p.currency_pair in ["btc_jpy", "eth_jpy", "xym_jpy"]
        ]
        return supported_pairs
