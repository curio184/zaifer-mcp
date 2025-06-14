"""
Zaifer MCP 価格チャートツール

Zaif APIの価格チャートデータ関連機能をMCPツールとして公開する実装
"""
from mcp.server.fastmcp import FastMCP
from zaifer_mcp.api.client import ZaifApi
from zaifer_mcp.models import PriceChartData, SupportedPair, SupportedPeriod
from datetime import datetime


def register_chart_tools(mcp: FastMCP, api: ZaifApi):
    """
    Zaifの価格チャート情報APIをMCPツールとして登録する
    
    Args:
        mcp: FastMCPインスタンス
        api: ZaifApiインスタンス
    """
    @mcp.tool()
    def get_price_chart(currency_pair: SupportedPair, timeframe: SupportedPeriod, start_date: str, end_date: str) -> PriceChartData:
        """
        指定期間の価格チャートデータを取得し、投資判断やトレンド分析に活用します。
        
        このツールは以下の用途で使用されます：
        - 価格トレンドの分析とパターン認識
        - 買い時・売り時の判断材料として
        - サポート・レジスタンスレベルの特定
        - テクニカル分析（移動平均、RSI等の計算基礎データ）
        - 価格変動の要因分析
        
        期間指定のガイドライン:
        - 1分足・5分足: 数時間～1日分のデータが適切です
        - 1時間足: 1週間～1ヶ月分のデータが適切です
        - 日足: 1ヶ月～6ヶ月分のデータが適切です
        - 週足: 6ヶ月～2年分のデータが適切です
        
        注意: 極端に長い期間（例: 1分足で1年分）を指定すると、
        データ量が膨大になり処理に時間がかかる場合があります。
        
        Args:
            currency_pair: 通貨ペア（'btc_jpy': ビットコイン/円、'eth_jpy': イーサリアム/円、'xym_jpy': シンボル/円）
            timeframe: 時間足（'1': 1分足、'5': 5分足、'15': 15分足、'30': 30分足、'60': 1時間足、
                      '240': 4時間足、'480': 8時間足、'720': 12時間足、'D': 日足、'W': 週足）
            start_date: 開始日時（ISO形式: 'YYYY-MM-DDTHH:MM:SS'）
            end_date: 終了日時（ISO形式: 'YYYY-MM-DDTHH:MM:SS'）
        
        Returns:
            PriceChartData: 価格チャートデータ
                - currency_pair: 通貨ペア
                - timeframe: 時間足の表示名（例: '1時間足'）
                - start_date: 開始日時（ISO 8601形式）
                - end_date: 終了日時（ISO 8601形式）
                - candlesticks: ローソク足データのリスト（時系列順）
                    - timestamp: ISO 8601形式の日時文字列
                    - open_price: 始値
                    - high_price: 高値
                    - low_price: 安値
                    - close_price: 終値
                    - volume: 出来高
                - data_count: データ件数
        
        Raises:
            ValueError: 日付形式が不正な場合や、APIエラーが発生した場合
        """
        try:
            from_dt = datetime.fromisoformat(start_date)
            to_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise ValueError("日付形式が不正です。'YYYY-MM-DDTHH:MM:SS'形式で指定してください。")
            
        # APIからデータを取得
        api_response = api.chart.get_ohlc(
            currency_pair=currency_pair,
            period=timeframe,
            from_datetime=from_dt,
            to_datetime=to_dt
        )
        
        # 新しいモデル形式に変換
        return PriceChartData.from_dict(
            data=api_response.to_dict(),
            currency_pair=currency_pair,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
