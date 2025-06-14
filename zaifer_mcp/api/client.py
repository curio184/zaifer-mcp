"""
Zaifer MCP API クライアント

Zaif暗号資産取引所のAPIにアクセスするためのクライアント実装
"""

import requests
from decimal import Decimal
from datetime import datetime
import hmac
import hashlib
import time
from typing import Dict, List, Any, Optional, Union


class NonceGenerator:
    """
    ノンスを生成します。
    """

    @staticmethod
    def generate() -> Decimal:
        """
        ノンスを生成します。
        タイムスタンプとマイクロ秒を組み合わせて一意の値を生成します。
        """
        now = datetime.now()
        datetime_part = str(int(time.mktime(now.timetuple())))
        second_part = "{0:06d}".format(now.microsecond)

        return Decimal(datetime_part + "." + second_part)


class ApiKeyAuthProvider:
    """
    API認証情報プロバイダー

    Zaif APIの認証に必要なAPIキーとシークレットを管理します。
    """

    def __init__(self, api_key: str, api_secret: str):
        """
        初期化

        Args:
            api_key: APIキー
            api_secret: APIシークレット
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def get_auth_headers(self, params: Dict[str, Any] = None) -> Dict[str, str]:
        """
        認証ヘッダーを取得

        Args:
            params: リクエストパラメータ

        Returns:
            認証ヘッダー
        """
        if not params:
            params = {}

        # NonceGeneratorを使用してnonceを生成
        params["nonce"] = str(NonceGenerator.generate())

        # URLエンコードされたパラメータを作成
        from urllib.parse import urlencode

        encoded_params = urlencode(params)

        # 署名を生成
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            encoded_params.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        return {"key": self.api_key, "sign": signature}


class HttpClient:
    """
    HTTPクライアント

    HTTPリクエストを実行するための汎用クライアント
    """

    def __init__(self, auth_provider: Optional[ApiKeyAuthProvider] = None):
        """
        初期化

        Args:
            auth_provider: 認証情報プロバイダー（認証が必要なAPIで使用）
        """
        self.auth_provider = auth_provider

    def get(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        GETリクエストを送信

        Args:
            url: リクエスト先のURL
            params: リクエストパラメータ

        Returns:
            レスポンス

        Raises:
            ValueError: HTTPエラーが発生した場合
        """
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Connection error: Could not connect to server")
        except requests.exceptions.Timeout:
            raise ValueError(f"Timeout error: Request timed out")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request error: {str(e)}")
        except ValueError:
            raise  # JSONデコードエラーなど
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    def post(
        self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        POSTリクエストを送信（認証が必要なAPI）

        Args:
            url: リクエスト先のURL
            params: リクエストパラメータ
            headers: リクエストヘッダー

        Returns:
            レスポンス

        Raises:
            ValueError: 認証情報が設定されていない、またはHTTPエラーが発生した場合
        """
        if not self.auth_provider:
            raise ValueError(
                "認証情報が設定されていません。ZAIF_API_KEYとZAIF_API_SECRETを環境変数に設定してください。"
            )

        if not params:
            params = {}

        # 認証ヘッダーを取得
        auth_headers = self.auth_provider.get_auth_headers(params)

        # ヘッダーをマージ
        if headers:
            headers.update(auth_headers)
        else:
            headers = auth_headers

        # URLエンコードされたパラメータを作成
        from urllib.parse import urlencode

        encoded_params = urlencode(params)

        try:
            # URLエンコードされたデータを送信
            response = requests.post(url, data=encoded_params, headers=headers)
            response.raise_for_status()

            result = response.json()

            # 元のzaiferと同様のレスポンス処理
            if result.get("success") == 0:
                error_msg = result.get("error", "Unknown error")
                raise ValueError(f"API error: {error_msg}")

            # 成功した場合は'return'キーの値を返す
            if "return" in result:
                return result["return"]

            return result
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Connection error: Could not connect to server")
        except requests.exceptions.Timeout:
            raise ValueError(f"Timeout error: Request timed out")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request error: {str(e)}")
        except ValueError:
            raise  # 既に適切なエラーメッセージが設定されている
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")


from zaifer_mcp.models.market import (
    Ticker,
    OrderBook,
    TradeHistory,
    Currency,
    CurrencyPair,
    LastPrice,
)


class MarketApi:
    """
    市場情報API

    Zaifの市場情報APIにアクセスするためのクラス
    """

    def __init__(self, http: HttpClient, base_url: str = "https://api.zaif.jp/api"):
        """
        初期化

        Args:
            http: HTTPクライアント
            base_url: APIのベースURL
        """
        self.http = http
        self.base_url = base_url

    def get_ticker(self, currency_pair: str) -> Ticker:
        """
        ティッカー情報を取得

        Args:
            currency_pair: 通貨ペア（例: 'btc_jpy'）

        Returns:
            Tickerオブジェクト
        """
        url = f"{self.base_url}/1/ticker/{currency_pair}"
        data = self.http.get(url)
        return Ticker.from_dict(data)

    def get_depth(self, currency_pair: str) -> OrderBook:
        """
        板情報を取得

        Args:
            currency_pair: 通貨ペア（例: 'btc_jpy'）

        Returns:
            OrderBookオブジェクト
        """
        url = f"{self.base_url}/1/depth/{currency_pair}"
        data = self.http.get(url)
        return OrderBook.from_dict(data)

    def get_currencies(self, currency: str = "all") -> List[Currency]:
        """
        通貨情報を取得

        Args:
            currency: 通貨コード、または'all'

        Returns:
            通貨情報のリスト
        """
        if currency == "all":
            url = f"{self.base_url}/1/currencies/all"
        else:
            url = f"{self.base_url}/1/currencies/{currency}"
        data = self.http.get(url)
        return [Currency.from_dict(item) for item in data]

    def get_currency_pairs(self, currency_pair: str = "all") -> List[CurrencyPair]:
        """
        通貨ペア情報を取得

        Args:
            currency_pair: 通貨ペア、または'all'

        Returns:
            通貨ペア情報のリスト
        """
        if currency_pair == "all":
            url = f"{self.base_url}/1/currency_pairs/all"
        else:
            url = f"{self.base_url}/1/currency_pairs/{currency_pair}"
        data = self.http.get(url)

        return [CurrencyPair.from_dict(item) for item in data]


from zaifer_mcp.models.account import (
    AccountBalance,
    UserProfile,
    UserIdentification,
    DepositRecords,
    WithdrawalRecords,
    WithdrawalResult,
)


class AccountApi:
    """
    アカウント情報API

    Zaifのアカウント情報APIにアクセスするためのクラス
    """

    def __init__(self, http: HttpClient, base_url: str = "https://api.zaif.jp/tapi"):
        """
        初期化

        Args:
            http: HTTPクライアント
            base_url: APIのベースURL
        """
        self.http = http
        self.base_url = base_url

    def get_info(self) -> AccountBalance:
        """
        残高情報を取得

        Returns:
            AccountBalanceオブジェクト
        """
        params = {"method": "get_info"}
        data = self.http.post(self.base_url, params)
        return AccountBalance.from_dict(data)

    def get_personal_info(self) -> UserProfile:
        """
        個人情報を取得

        Returns:
            UserProfileオブジェクト
        """
        params = {"method": "get_personal_info"}
        data = self.http.post(self.base_url, params)
        return UserProfile.from_dict(data)

    def get_deposit_history(
        self,
        currency: str,
        count: int = None,
        from_timestamp: int = None,
        end_timestamp: int = None,
    ) -> DepositRecords:
        """
        入金履歴を取得

        Args:
            currency: 通貨コード
            count: 取得数
            from_timestamp: 開始タイムスタンプ
            end_timestamp: 終了タイムスタンプ

        Returns:
            DepositRecordsオブジェクト
        """
        params = {"currency": currency}

        if count is not None:
            params["count"] = count

        if from_timestamp is not None:
            params["from"] = from_timestamp

        if end_timestamp is not None:
            params["end"] = end_timestamp

        params["method"] = "deposit_history"
        data = self.http.post(self.base_url, params)
        return DepositRecords.from_dict(data)

    def get_withdraw_history(
        self,
        currency: str,
        count: int = None,
        from_timestamp: int = None,
        end_timestamp: int = None,
    ) -> WithdrawalRecords:
        """
        出金履歴を取得

        Args:
            currency: 通貨コード
            count: 取得数
            from_timestamp: 開始タイムスタンプ
            end_timestamp: 終了タイムスタンプ

        Returns:
            WithdrawalRecordsオブジェクト
        """
        params = {"currency": currency}

        if count is not None:
            params["count"] = count

        if from_timestamp is not None:
            params["from"] = from_timestamp

        if end_timestamp is not None:
            params["end"] = end_timestamp

        params["method"] = "withdraw_history"
        data = self.http.post(self.base_url, params)
        return WithdrawalRecords.from_dict(data)


from zaifer_mcp.models.trade import OrderResponse, OpenOrderList, CancelOrderResponse, TradeExecutionList


class TradeApi:
    """
    取引API

    Zaifの取引APIにアクセスするためのクラス
    """

    def __init__(self, http: HttpClient, base_url: str = "https://api.zaif.jp/tapi"):
        """
        初期化

        Args:
            http: HTTPクライアント
            base_url: APIのベースURL
        """
        self.http = http
        self.base_url = base_url

    def open_order(
        self,
        currency_pair: str,
        action: str,
        price: Union[int, float, Decimal],
        amount: Union[int, float, Decimal],
    ) -> OrderResponse:
        """
        注文を発注

        Args:
            currency_pair: 通貨ペア（例: 'btc_jpy'）
            action: 注文タイプ（'bid': 買い、'ask': 売り）
            price: 価格
            amount: 数量

        Returns:
            OrderResponseオブジェクト
        """
        params = {
            "currency_pair": currency_pair,
            "action": action,
            "price": float(price),
            "amount": float(amount),
        }

        params["method"] = "trade"
        data = self.http.post(self.base_url, params)
        return OrderResponse.from_dict(data)

    def cancel_order(
        self, order_id: int, currency_pair: str = None, is_token: bool = None
    ) -> CancelOrderResponse:
        """
        注文をキャンセル

        Args:
            order_id: 注文ID
            currency_pair: 通貨ペア
            is_token: トークン種別（トークンの場合True）

        Returns:
            CancelOrderResponseオブジェクト

        Note:
            TODO: MCP利用者にis_tokenパラメータを意識させないように隠蔽する方法を検討する。
            将来的には通貨ペアやorder_idから自動的にトークン種別を判定する機能を実装するか、
            または内部的にAPIを呼び分けるなどの方法で対応する。
        """
        params = {"order_id": order_id}

        if currency_pair:
            params["currency_pair"] = currency_pair

        if is_token is not None:
            params["is_token"] = is_token

        params["method"] = "cancel_order"
        data = self.http.post(self.base_url, params)
        return CancelOrderResponse.from_dict(data)

    def get_active_orders(self, currency_pair: str = None) -> OpenOrderList:
        """
        有効な注文一覧を取得

        Args:
            currency_pair: 通貨ペア

        Returns:
            OpenOrderListオブジェクト
        """
        params = {}

        if currency_pair:
            params["currency_pair"] = currency_pair

        params["method"] = "active_orders"
        data = self.http.post(self.base_url, params)
        return OpenOrderList.from_dict(data)

    def get_trade_history(
        self,
        currency_pair: str = None,
        count: int = None,
        from_timestamp: int = None,
        end_timestamp: int = None,
    ) -> TradeExecutionList:
        """
        取引履歴を取得

        Args:
            currency_pair: 通貨ペア
            count: 取得数
            from_timestamp: 開始タイムスタンプ
            end_timestamp: 終了タイムスタンプ

        Returns:
            TradeExecutionListオブジェクト
        """
        params = {}

        if currency_pair:
            params["currency_pair"] = currency_pair

        if count is not None:
            params["count"] = count

        if from_timestamp is not None:
            params["since"] = from_timestamp

        if end_timestamp is not None:
            params["end"] = end_timestamp

        params["method"] = "trade_history"
        data = self.http.post(self.base_url, params)
        return TradeExecutionList.from_dict(data)


from zaifer_mcp.models.chart import PriceChartData


class ChartApi:
    """
    チャート情報API

    Zaifのチャート情報APIにアクセスするためのクラス
    """

    def __init__(
        self, http: HttpClient, base_url: str = "https://zaif.jp/zaif_chart_api/v1"
    ):
        """
        初期化

        Args:
            http: HTTPクライアント
            base_url: APIのベースURL
        """
        self.http = http
        self.base_url = base_url

    def get_ohlc(
        self,
        currency_pair: str,
        period: str,
        from_datetime: datetime,
        to_datetime: datetime,
    ) -> PriceChartData:
        """
        価格チャートデータを取得

        Args:
            currency_pair: 通貨ペア（例: 'btc_jpy'）
            period: 期間（1分足:1、5分足:5、15分足:15、30分足:30、1時間足:60、
                   4時間足:240、8時間足:480、12時間足:720、1日足:D、1週足:W）
            from_datetime: 開始日時
            to_datetime: 終了日時

        Returns:
            PriceChartDataオブジェクト
        """
        params = {
            "symbol": currency_pair,
            "resolution": period,
            "from": int(from_datetime.timestamp()),
            "to": int(to_datetime.timestamp()),
        }

        url = f"{self.base_url}/history"
        response = self.http.get(url, params)

        # Zaifチャート履歴APIはJSONエンコードされた文字列を返すため、追加のパースが必要
        if isinstance(response, str):
            import json

            data = json.loads(response)
        else:
            data = response
        return PriceChartData.from_dict(
            data, 
            currency_pair, 
            period, 
            from_datetime.isoformat(), 
            to_datetime.isoformat()
        )


class ZaifApi:
    """
    Zaif API クライアント

    Zaif暗号資産取引所のAPIにアクセスするためのクライアント
    """

    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        market_api_url: str = "https://api.zaif.jp/api",
        trade_api_url: str = "https://api.zaif.jp/tapi",
        chart_api_url: str = "https://zaif.jp/zaif_chart_api/v1",
    ):
        """
        初期化

        Args:
            api_key: APIキー（認証が必要なAPIで使用）
            api_secret: APIシークレット（認証が必要なAPIで使用）
            market_api_url: 市場情報APIのベースURL
            trade_api_url: 取引APIのベースURL
            chart_api_url: チャートAPIのベースURL
        """
        auth_provider = None
        if api_key and api_secret:
            auth_provider = ApiKeyAuthProvider(api_key, api_secret)

        self.http = HttpClient(auth_provider)
        self.market = MarketApi(self.http, market_api_url)
        self.account = AccountApi(self.http, trade_api_url)
        self.trade = TradeApi(self.http, trade_api_url)
        self.chart = ChartApi(self.http, chart_api_url)
