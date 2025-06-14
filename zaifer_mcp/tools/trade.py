"""
Zaifer MCP 取引ツール

Zaif APIの取引関連機能をMCPツールとして公開する実装
"""

from mcp.server.fastmcp import FastMCP
from zaifer_mcp.api.client import ZaifApi
from zaifer_mcp.models import (
    OrderResponse,
    CancelOrderResponse,
    OpenOrderList,
    SupportedPair,
    TradeExecutionList,
    OrderType,
)
from decimal import Decimal
from datetime import datetime


def register_trade_tools(mcp: FastMCP, api: ZaifApi):
    """
    Zaifの取引APIをMCPツールとして登録する

    Args:
        mcp: FastMCPインスタンス
        api: ZaifApiインスタンス
    """

    @mcp.tool()
    def place_order(
        currency_pair: SupportedPair,
        order_type: OrderType,
        price: float,
        quantity: float,
    ) -> OrderResponse:
        """
        暗号資産の売買注文を発注します。

        このツールは、指定した通貨ペアで新規の売買注文を市場に出すために使用します。
        価格と数量を指定して、指値注文を出すことができます。

        使用例:
        - ビットコインを指定価格で購入したい場合
        - イーサリアムを売却して利益を確定したい場合
        - 特定の価格で指値注文を出したい場合

        注意: このツールを使用するには、環境変数にAPIキーとシークレットが設定されている必要があります。

        Args:
            currency_pair: 取引する通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）
            order_type: 注文タイプ（'bid': 買い注文、'ask': 売り注文）
            price: 注文価格（日本円）- 指値注文の場合の1単位あたりの価格
            quantity: 注文数量 - 売買する暗号資産の量（例: ビットコインの場合は0.01BTCなど）

        Returns:
            OrderResponse: 注文結果情報
                - filled_amount: 即時約定した数量
                - unfilled_amount: 未約定の残り数量
                - order_id: 注文ID（全約定の場合は0）
                - balances: 注文後の各通貨の残高情報

        Raises:
            ValueError: 認証情報が設定されていない場合や、APIエラーが発生した場合
        """
        if not api.trade.http.auth_provider:
            raise ValueError(
                "認証情報が設定されていません。APIキーとシークレットを.envファイルに設定してください。"
            )

        return api.trade.open_order(
            currency_pair=currency_pair,
            action=order_type,  # APIの引数名は変更できないのでマッピング
            price=Decimal(str(price)),
            amount=Decimal(str(quantity)),  # APIの引数名は変更できないのでマッピング
        )

    @mcp.tool()
    def cancel_order(
        order_id: int, currency_pair: SupportedPair = None
    ) -> CancelOrderResponse:
        """
        未約定の暗号資産取引注文をキャンセルします。

        このツールは、既に発注済みで未約定（一部約定を含む）の注文をキャンセルするために使用します。
        注文IDを指定してキャンセルでき、任意で通貨ペアも指定できます。

        使用例:
        - 価格変動により注文戦略を変更したい場合
        - 誤った注文をキャンセルしたい場合
        - 長時間約定しない注文を取り消したい場合

        注意: このツールを使用するには、環境変数にAPIキーとシークレットが設定されている必要があります。

        Args:
            order_id: キャンセルする注文のID（get_open_ordersで取得可能）
            currency_pair: 通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）
                          指定しない場合、システムは注文IDから自動的に判断します

        Returns:
            CancelOrderResponse: キャンセル結果情報
                - order_id: キャンセルした注文ID
                - balances: キャンセル後の各通貨の残高情報

        Raises:
            ValueError: 認証情報が設定されていない場合や、APIエラーが発生した場合
        """
        if not api.trade.http.auth_provider:
            raise ValueError(
                "認証情報が設定されていません。APIキーとシークレットを.envファイルに設定してください。"
            )

        return api.trade.cancel_order(order_id, currency_pair)

    @mcp.tool()
    def get_open_orders(currency_pair: SupportedPair = None) -> OpenOrderList:
        """
        現在有効な（未約定の）暗号資産取引注文一覧を取得します。

        このツールは、現在板に出ている未約定注文（一部約定を含む）の一覧を確認するために使用します。
        特定の通貨ペアでフィルタリングすることも、すべての通貨ペアの注文を取得することもできます。

        使用例:
        - 現在の注文状況を確認したい場合
        - キャンセルすべき注文を特定したい場合
        - 注文戦略の進捗を確認したい場合

        注意: このツールを使用するには、環境変数にAPIキーとシークレットが設定されている必要があります。

        Args:
            currency_pair: 通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）
                          指定しない場合、すべての通貨ペアの注文が返されます

        Returns:
            OpenOrderList: 未約定注文一覧
                - open_orders: 注文IDをキーとする注文情報の辞書
                    - currency_pair: 通貨ペア
                    - order_type: 注文タイプ（'bid': 買い、'ask': 売り）
                    - price: 注文価格
                    - quantity: 注文数量
                    - order_time: 注文日時のISO 8601形式の文字列（例: '2023-05-24T15:30:45+09:00'）

        Raises:
            ValueError: 認証情報が設定されていない場合や、APIエラーが発生した場合
        """
        if not api.trade.http.auth_provider:
            raise ValueError(
                "認証情報が設定されていません。APIキーとシークレットを.envファイルに設定してください。"
            )

        orders = api.trade.get_active_orders(currency_pair)

        # 対応している通貨ペアのみをフィルタリング
        if orders.open_orders:
            filtered_orders = {}
            for order_id, order in orders.open_orders.items():
                if order.currency_pair in ["btc_jpy", "eth_jpy", "xym_jpy"]:
                    filtered_orders[order_id] = order

            # 元のオブジェクトのopen_ordersを置き換え
            orders.open_orders = filtered_orders

        return orders

    @mcp.tool()
    def get_trade_executions(
        currency_pair: SupportedPair = None,
        limit: int = 20,
        start_date: str = "",
        end_date: str = "",
    ) -> TradeExecutionList:
        """
        あなたのアカウントで約定（成立）した取引履歴を取得します。

        このツールは、実際に成立した売買取引の記録を確認するために使用します。
        特定の通貨ペアだけの履歴を見たり、取得件数や期間を指定して絞り込んだりできます。

        使用例:
        - 過去1ヶ月の取引履歴を確認して収益を計算したい場合
        - ビットコイン取引だけを分析したい場合
        - 最近の20件の取引を確認して取引戦略の成果を評価したい場合
        - 税金申告のために年間の取引記録を取得したい場合

        注意: このツールを使用するには、環境変数にAPIキーとシークレットが設定されている必要があります。

        Args:
            currency_pair: 取引通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）
                          指定しない場合、すべての通貨ペアの取引履歴が返されます
            limit: 取得する履歴の最大件数（例: 10, 20, 50）
            start_date: この日付以降の取引を取得（例: '2023-01-01'）
            end_date: この日付以前の取引を取得（例: '2023-12-31'）

        Returns:
            TradeExecutionList: 約定済み取引履歴
                - executions: 約定済み取引のリスト（新しい順）
                    - execution_id: 取引ID（約定ID）
                    - currency_pair: 通貨ペア（例: 'btc_jpy'）
                    - trade_side: 取引であなたが行った行動（'buy': 買い、'sell': 売り、'self': 自己取引）
                    - market_role: 取引における役割（'maker': 注文を出して待っていた側、'taker': 即時約定した側、'both': 自己取引の場合）
                    - price: 約定価格（日本円）
                    - quantity: 約定数量（暗号資産の量）
                    - fee_amount: 支払った手数料の金額（日本円）
                    - execution_time: 約定日時（ISO 8601形式の文字列、例: '2023-05-24T15:30:45+09:00'）

        Raises:
            ValueError: 認証情報が設定されていない場合や、APIエラーが発生した場合
        """
        if not api.trade.http.auth_provider:
            raise ValueError(
                "認証情報が設定されていません。APIキーとシークレットを.envファイルに設定してください。"
            )

        # 対応している通貨ペアのみを許可
        if currency_pair is not None and currency_pair not in [
            "btc_jpy",
            "eth_jpy",
            "xym_jpy",
        ]:
            raise ValueError(f"サポートされていない通貨ペアです: {currency_pair}")

        # 日付文字列をUNIXタイムスタンプに変換
        from_timestamp = None
        if start_date:  # 空文字列はFalsyなので、この条件で十分
            from_timestamp = int(datetime.fromisoformat(start_date).timestamp())

        end_timestamp = None
        if end_date:  # 空文字列はFalsyなので、この条件で十分
            # 終了日の23:59:59を指定（その日の最後まで含める）
            end_date_obj = datetime.fromisoformat(end_date)
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
            end_timestamp = int(end_date_obj.timestamp())

        trade_history = api.trade.get_trade_history(
            currency_pair=currency_pair,
            count=limit,
            from_timestamp=from_timestamp,
            end_timestamp=end_timestamp,
        )

        # 対応している通貨ペアのみをフィルタリング
        if trade_history.executions:
            filtered_executions = [
                execution
                for execution in trade_history.executions
                if execution.currency_pair in ["btc_jpy", "eth_jpy", "xym_jpy"]
            ]

            # 元のオブジェクトのexecutionsを置き換え
            trade_history.executions = filtered_executions

        return trade_history
