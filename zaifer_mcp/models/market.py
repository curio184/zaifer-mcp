"""
市場情報に関するデータモデルを提供します。
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Tuple, ClassVar, Optional
from datetime import datetime


@dataclass
class Currency:
    """
    通貨情報を表すデータクラス。
    
    Attributes:
        name: 通貨の名前
        is_token: トークン種別（トークンの場合True）
    """
    name: str
    is_token: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Currency':
        """
        APIレスポンスからCurrencyインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            Currencyインスタンス
        """
        return cls(
            name=data['name'],
            is_token=data['is_token']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Currencyインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'name': self.name,
            'is_token': self.is_token
        }


@dataclass
class CurrencyPair:
    """
    LLM向けに最適化された通貨ペア制約情報を表すデータクラス。
    
    Attributes:
        currency_pair: 通貨ペア識別子（例: 'btc_jpy'）
        min_quantity: 最小注文数量
        quantity_step: 注文数量の刻み幅
        min_price: 最小注文価格
        price_step: 注文価格の刻み幅
        price_precision: 価格表示の小数点桁数
        display_name: 表示用名称（例: 'ビットコイン/円'）
    """
    currency_pair: str
    min_quantity: Decimal
    quantity_step: Decimal
    min_price: Decimal
    price_step: Decimal
    price_precision: int
    display_name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurrencyPair':
        """
        APIレスポンスからCurrencyPairインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            CurrencyPairインスタンス
        """
        # display_nameを基軸通貨名/決済通貨名の形式で生成
        base_currency_name = data['item_japanese']
        quote_currency_name = data['aux_japanese']
        display_name = f"{base_currency_name}/{quote_currency_name}"
        
        return cls(
            currency_pair=data['currency_pair'],
            min_quantity=Decimal(str(data['item_unit_min'])),
            quantity_step=Decimal(str(data['item_unit_step'])),
            min_price=Decimal(str(data['aux_unit_min'])),
            price_step=Decimal(str(data['aux_unit_step'])),
            price_precision=int(data['aux_unit_point']),
            display_name=display_name
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        CurrencyPairインスタンスを辞書に変換します。
        
        Returns:
            LLM向けに最適化された辞書
        """
        return {
            'currency_pair': self.currency_pair,
            'min_quantity': str(self.min_quantity),
            'quantity_step': str(self.quantity_step),
            'min_price': str(self.min_price),
            'price_step': str(self.price_step),
            'price_precision': self.price_precision,
            'display_name': self.display_name
        }


@dataclass
class LastPrice:
    """
    現在の終値を表すデータクラス。
    
    Attributes:
        last_price: 現在の終値
    """
    last_price: Decimal
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LastPrice':
        """
        APIレスポンスからLastPriceインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            LastPriceインスタンス
        """
        return cls(
            last_price=Decimal(str(data['last_price']))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        LastPriceインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'last_price': str(self.last_price)
        }


@dataclass
class Ticker:
    """
    ティッカー情報を表すデータクラス。
    
    Attributes:
        last_price: 最終取引価格
        high_price: 最高値（24時間）
        low_price: 最安値（24時間）
        ask_price: 売り注文最安値
        bid_price: 買い注文最高値
        volume: 24時間取引量
    """
    last_price: Decimal
    high_price: Decimal
    low_price: Decimal
    ask_price: Decimal
    bid_price: Decimal
    volume: Decimal
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticker':
        """
        APIレスポンスからTickerインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            Tickerインスタンス
        """
        return cls(
            last_price=Decimal(str(data['last'])),
            high_price=Decimal(str(data['high'])),
            low_price=Decimal(str(data['low'])),
            ask_price=Decimal(str(data['ask'])),
            bid_price=Decimal(str(data['bid'])),
            volume=Decimal(str(data['volume']))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        TickerインスタンスをAPIレスポンス形式の辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'last': str(self.last_price),
            'high': str(self.high_price),
            'low': str(self.low_price),
            'ask': str(self.ask_price),
            'bid': str(self.bid_price),
            'volume': str(self.volume)
        }


@dataclass
class OrderBookItem:
    """
    板情報の1アイテムを表すデータクラス。
    
    Attributes:
        price: 価格
        quantity: 数量
    """
    price: Decimal
    quantity: Decimal


@dataclass
class OrderBook:
    """
    板情報を表すデータクラス。
    
    Attributes:
        asks: 売り注文リスト
        bids: 買い注文リスト
    """
    asks: List[OrderBookItem]
    bids: List[OrderBookItem]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderBook':
        """
        APIレスポンスからOrderBookインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            OrderBookインスタンス
        """
        asks = [OrderBookItem(Decimal(str(item[0])), Decimal(str(item[1]))) 
                for item in data.get('asks', [])]
        bids = [OrderBookItem(Decimal(str(item[0])), Decimal(str(item[1]))) 
                for item in data.get('bids', [])]
        return cls(asks=asks, bids=bids)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        OrderBookインスタンスをAPIレスポンス形式の辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'asks': [[str(item.price), str(item.quantity)] for item in self.asks],
            'bids': [[str(item.price), str(item.quantity)] for item in self.bids]
        }


@dataclass
class TradeHistoryItem:
    """
    取引履歴の1アイテムを表すデータクラス。
    
    Attributes:
        date: UNIXタイムスタンプ
        price: 価格
        amount: 数量
        trade_type: 取引タイプ（ask/bid）
    """
    date: int
    price: Decimal
    amount: Decimal
    trade_type: str
    
    @property
    def datetime(self) -> datetime:
        """
        UNIXタイムスタンプをdatetimeに変換します。
        
        Returns:
            datetime形式の日時
        """
        return datetime.fromtimestamp(self.date)


@dataclass
class TradeHistory:
    """
    取引履歴を表すデータクラス。
    
    Attributes:
        items: 取引履歴アイテムのリスト
    """
    items: List[TradeHistoryItem]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> 'TradeHistory':
        """
        APIレスポンスからTradeHistoryインスタンスを作成します。
        
        Args:
            data: APIレスポンスのリスト
            
        Returns:
            TradeHistoryインスタンス
        """
        items = [
            TradeHistoryItem(
                date=int(item['date']),
                price=Decimal(str(item['price'])),
                amount=Decimal(str(item['amount'])),
                trade_type=item['trade_type']
            )
            for item in data
        ]
        return cls(items=items)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        TradeHistoryインスタンスをAPIレスポンス形式のリストに変換します。
        
        Returns:
            APIレスポンス形式のリスト
        """
        return [
            {
                'date': item.date,
                'price': str(item.price),
                'amount': str(item.amount),
                'trade_type': item.trade_type
            }
            for item in self.items
        ]
