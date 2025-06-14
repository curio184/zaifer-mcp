"""
共通のデータ型や定数を定義するモジュール
"""
from typing import Literal

# 対応する通貨ペアを明示的に制限
SupportedPair = Literal["btc_jpy", "eth_jpy", "xym_jpy"]

# 対応する通貨を明示的に制限
SupportedCurrency = Literal["btc", "eth", "xym", "jpy"]

# 対応する期間を明示的に制限
SupportedPeriod = Literal["1", "5", "15", "30", "60", "240", "480", "720", "D", "W"]

# 注文タイプ
OrderType = Literal["bid", "ask"]
