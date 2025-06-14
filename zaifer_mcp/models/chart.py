"""
価格チャート情報に関するデータモデルを提供します。
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class CandlestickData:
    """
    ローソク足の個別データ（1つの時間足分の価格情報）を表すデータクラス。
    
    Attributes:
        timestamp: ISO 8601形式の日時文字列
        open_price: 始値（期間開始時の価格）
        high_price: 高値（期間中の最高価格）
        low_price: 安値（期間中の最低価格）
        close_price: 終値（期間終了時の価格）
        volume: 出来高（期間中の取引量）
    """
    timestamp: str
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    


@dataclass
class PriceChartData:
    """
    価格チャートデータ全体を表すデータクラス。
    get_price_chartの戻り値に対応します。
    
    Attributes:
        currency_pair: 通貨ペア（例: 'btc_jpy'）
        timeframe: 時間足（例: '1時間足'）
        start_date: 開始日時（ISO 8601形式）
        end_date: 終了日時（ISO 8601形式）
        candlesticks: ローソク足データ（時系列順）
        data_count: データ件数
    """
    currency_pair: str
    timeframe: str
    start_date: str
    end_date: str
    candlesticks: List[CandlestickData]
    data_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], currency_pair: str, timeframe: str, start_date: str, end_date: str) -> 'PriceChartData':
        """
        APIレスポンスからPriceChartDataインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            currency_pair: 通貨ペア
            timeframe: 時間足
            start_date: 開始日時（ISO 8601形式）
            end_date: 終了日時（ISO 8601形式）
            
        Returns:
            PriceChartDataインスタンス
        """
        candlesticks = []
        for item in data.get('ohlc_data', []):
            # ミリ秒単位のタイムスタンプをISO 8601形式に変換
            timestamp_ms = int(item.get('time', 0))
            timestamp_iso = datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
            
            candlesticks.append(CandlestickData(
                timestamp=timestamp_iso,
                open_price=Decimal(str(item.get('open', '0'))),
                high_price=Decimal(str(item.get('high', '0'))),
                low_price=Decimal(str(item.get('low', '0'))),
                close_price=Decimal(str(item.get('close', '0'))),
                volume=Decimal(str(item.get('volume', '0')))
            ))
        
        # 時間足の表示名を生成
        timeframe_names = {
            "1": "1分足", "5": "5分足", "15": "15分足", "30": "30分足",
            "60": "1時間足", "240": "4時間足", "480": "8時間足", 
            "720": "12時間足", "D": "日足", "W": "週足"
        }
        timeframe_display = timeframe_names.get(timeframe, f"{timeframe}足")
        
        return cls(
            currency_pair=currency_pair,
            timeframe=timeframe_display,
            start_date=start_date,
            end_date=end_date,
            candlesticks=candlesticks,
            data_count=int(data.get('data_count', 0))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        PriceChartDataインスタンスをAPIレスポンス形式の辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'ohlc_data': [
                {
                    'time': int(datetime.fromisoformat(item.timestamp).timestamp() * 1000),
                    'open': str(item.open_price),
                    'high': str(item.high_price),
                    'low': str(item.low_price),
                    'close': str(item.close_price),
                    'volume': str(item.volume)
                }
                for item in self.candlesticks
            ],
            'data_count': self.data_count
        }
