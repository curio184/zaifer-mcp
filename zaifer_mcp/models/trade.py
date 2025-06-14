"""
取引情報に関するデータモデルを提供します。
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class OrderResponse:
    """
    注文発注後のレスポンス情報を表すデータクラス。
    place_orderの戻り値に対応します。

    Attributes:
        filled_amount: 即時約定した数量（一部約定または全約定の場合の約定済み量）
        unfilled_amount: 未約定の残り数量（板に残った注文量）
        order_id: 注文ID（全約定時は0、未約定または一部約定時は注文を識別するID）
        balances: 注文後の各通貨の残高情報
    """

    filled_amount: Decimal
    unfilled_amount: Decimal
    order_id: int
    balances: Dict[str, Decimal]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderResponse":
        """
        APIレスポンスからOrderResponseインスタンスを作成します。

        Args:
            data: APIレスポンスの辞書

        Returns:
            OrderResponseインスタンス
        """
        balances = {k: Decimal(str(v)) for k, v in data.get("funds", {}).items()}
        return cls(
            filled_amount=Decimal(str(data.get("received", "0"))),
            unfilled_amount=Decimal(str(data.get("remains", "0"))),
            order_id=int(data.get("order_id", 0)),
            balances=balances,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        OrderResponseインスタンスを辞書に変換します。

        Returns:
            APIレスポンス形式の辞書
        """
        return {
            "received": str(self.filled_amount),
            "remains": str(self.unfilled_amount),
            "order_id": self.order_id,
            "funds": {k: str(v) for k, v in self.balances.items()},
        }


@dataclass
class OpenOrder:
    """
    未約定注文の情報を表すデータクラス。

    Attributes:
        currency_pair: 通貨ペア（例: 'btc_jpy'）
        order_type: 注文タイプ（'bid': 買い注文、'ask': 売り注文）
        price: 注文価格（通貨単位）
        quantity: 注文数量（暗号資産の量）
        order_time: 注文日時のISO 8601形式の文字列
    """

    currency_pair: str
    order_type: str
    price: Decimal
    quantity: Decimal
    order_time: str


@dataclass
class OpenOrderList:
    """
    未約定注文一覧を表すデータクラス。
    get_open_ordersの戻り値に対応します。

    Attributes:
        open_orders: 注文IDをキーとする未約定注文情報の辞書
    """

    open_orders: Dict[int, OpenOrder]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenOrderList":
        """
        APIレスポンスからOpenOrderListインスタンスを作成します。

        Args:
            data: APIレスポンスの辞書

        Returns:
            OpenOrderListインスタンス
        """
        open_orders = {}
        for order_id_str, order_data in data.items():
            if order_id_str.isdigit():  # 注文IDのみを処理
                order_id = int(order_id_str)
                open_orders[order_id] = OpenOrder(
                    currency_pair=order_data.get("currency_pair", ""),
                    order_type=order_data.get("action", ""),
                    price=Decimal(str(order_data.get("price", "0"))),
                    quantity=Decimal(str(order_data.get("amount", "0"))),
                    order_time=datetime.fromtimestamp(
                        int(order_data.get("timestamp", 0))
                    ).isoformat(),
                )
        return cls(open_orders=open_orders)

    def to_dict(self) -> Dict[str, Any]:
        """
        OpenOrderListインスタンスを辞書に変換します。

        Returns:
            APIレスポンス形式の辞書
        """
        result = {}
        for order_id, order_item in self.open_orders.items():
            result[str(order_id)] = {
                "currency_pair": order_item.currency_pair,
                "action": order_item.order_type,
                "price": str(order_item.price),
                "amount": str(order_item.quantity),
                "date": order_item.order_time,
            }
        return result


@dataclass
class CancelOrderResponse:
    """
    注文キャンセル結果を表すデータクラス。
    cancel_orderの戻り値に対応します。

    Attributes:
        order_id: キャンセルした注文ID
        balances: キャンセル後の各通貨の残高情報
    """

    order_id: int
    balances: Dict[str, Decimal]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CancelOrderResponse":
        """
        APIレスポンスからCancelOrderResponseインスタンスを作成します。

        Args:
            data: APIレスポンスの辞書

        Returns:
            CancelOrderResponseインスタンス
        """
        balances = {k: Decimal(str(v)) for k, v in data.get("funds", {}).items()}
        return cls(order_id=int(data.get("order_id", 0)), balances=balances)

    def to_dict(self) -> Dict[str, Any]:
        """
        CancelOrderResponseインスタンスを辞書に変換します。

        Returns:
            APIレスポンス形式の辞書
        """
        return {
            "order_id": self.order_id,
            "funds": {k: str(v) for k, v in self.balances.items()},
        }


@dataclass
class TradeExecution:
    """
    約定済み取引の情報を表すデータクラス。

    Attributes:
        execution_id: 取引ID（約定ID）
        currency_pair: 通貨ペア
        trade_side: 取引であなたが行った行動（'buy': 買い、'sell': 売り、'self': 自己取引）
        price: 約定価格
        quantity: 約定数量
        fee_amount: 支払った手数料の金額
        market_role: 取引における役割（'maker': 注文を出して待っていた側、'taker': 即時約定した側、'both': 自己取引の場合）
        execution_time: 約定日時のISO 8601形式の文字列
    """

    execution_id: int
    currency_pair: str
    trade_side: str
    price: Decimal
    quantity: Decimal
    fee_amount: Decimal
    market_role: str
    execution_time: Optional[str] = None


@dataclass
class TradeExecutionList:
    """
    約定済み取引履歴を表すデータクラス。
    get_trade_historyの戻り値に対応します。

    Attributes:
        executions: 約定済み取引のリスト
    """

    executions: List[TradeExecution]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeExecutionList":
        """
        APIレスポンスからTradeExecutionListインスタンスを作成します。

        Args:
            data: APIレスポンスの辞書（キーが取引ID、値が取引情報）

        Returns:
            TradeExecutionListインスタンス
        """
        executions = []
        for trade_id, item in data.items():
            if not isinstance(item, dict):
                continue  # 辞書でない項目はスキップ

            try:
                trade_id_int = int(trade_id)

                timestamp = item.get("timestamp")
                if timestamp is not None and timestamp != "":
                    execution_time = datetime.fromtimestamp(int(timestamp)).isoformat()
                else:
                    execution_time = None

                # action と your_action から trade_side と market_role を決定
                action = item.get("action", "")
                your_action = item.get("your_action", "")

                # trade_side の決定
                if your_action == "both":
                    trade_side = "self"
                elif your_action == "bid":
                    trade_side = "buy"
                elif your_action == "ask":
                    trade_side = "sell"
                else:
                    trade_side = "unknown"

                # market_role の決定
                if your_action == "both":
                    market_role = "both"
                elif (action == "bid" and your_action == "bid") or (
                    action == "ask" and your_action == "ask"
                ):
                    market_role = "taker"
                elif (action == "bid" and your_action == "ask") or (
                    action == "ask" and your_action == "bid"
                ):
                    market_role = "maker"
                else:
                    market_role = "unknown"

                executions.append(
                    TradeExecution(
                        execution_id=trade_id_int,
                        currency_pair=item.get("currency_pair", ""),
                        trade_side=trade_side,
                        price=Decimal(str(item.get("price", "0"))),
                        quantity=Decimal(str(item.get("amount", "0"))),
                        fee_amount=Decimal(str(item.get("fee", "0"))),
                        market_role=market_role,
                        execution_time=execution_time,
                    )
                )
            except (ValueError, TypeError, KeyError) as e:
                # 変換エラーが発生した場合はスキップ
                print(f"Warning: Failed to parse trade item {trade_id}: {e}")
        return cls(executions=executions)

    def to_dict(self) -> List[Dict[str, Any]]:
        """
        TradeExecutionListインスタンスをAPIレスポンス形式のリストに変換します。

        Returns:
            APIレスポンス形式のリスト
        """
        result = []
        for item in self.executions:
            trade_dict = {
                "id": item.execution_id,
                "currency_pair": item.currency_pair,
                "action": item.trade_side,  # APIの互換性のために元の名前を維持
                "price": str(item.price),
                "amount": str(item.quantity),
                "fee": str(item.fee_amount),
                "your_action": item.market_role,  # APIの互換性のために元の名前を維持
            }

            if item.execution_time is not None:
                trade_dict["timestamp"] = item.execution_time

            result.append(trade_dict)
        return result
