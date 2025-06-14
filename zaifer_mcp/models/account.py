"""
アカウント情報に関するデータモデルを提供します。
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Optional
from zaifer_mcp.models.common import SupportedCurrency

@dataclass
class WithdrawalResult:
    """
    出金依頼結果を表すデータクラス。
    withdraw の戻り値に対応します。
    
    Attributes:
        txid: トランザクションID
        balances: 出金後の各通貨の残高情報
    """
    txid: str
    balances: Dict[str, Decimal]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WithdrawalResult':
        """
        APIレスポンスからWithdrawalResultインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            WithdrawalResultインスタンス
        """
        balances = {k: Decimal(str(v)) for k, v in data.get('funds', {}).items()}
        return cls(
            txid=data.get('txid', ''),
            balances=balances
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        WithdrawalResultインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'txid': self.txid,
            'funds': {k: str(v) for k, v in self.balances.items()}
        }


@dataclass
class AccountBalance:
    """
    アカウント残高情報を表すデータクラス。
    get_info, get_info2の戻り値に対応します。
    
    Attributes:
        balances: 各通貨の残高情報
        permissions: 利用権限（get_infoのみ）
    """
    balances: Dict[str, Decimal]
    permissions: Optional[Dict[str, bool]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountBalance':
        """
        APIレスポンスからAccountBalanceインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            AccountBalanceインスタンス
        """
        balances = {k: Decimal(str(v)) for k, v in data.get('funds', {}).items()}
        permissions = data.get('rights')
        return cls(balances=balances, permissions=permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        AccountBalanceインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        result = {'funds': {k: str(v) for k, v in self.balances.items()}}
        if self.permissions is not None:
            result['rights'] = self.permissions
        return result


@dataclass
class UserProfile:
    """
    ユーザープロフィール情報を表すデータクラス。
    get_personal_infoの戻り値に対応します。
    
    Attributes:
        ranking_id: ランキングID（APIレスポンスではranking_nickname）
        icon_path: アイコンパス
        area_id: エリアID
        nickname: ニックネーム（APIレスポンスではranking_nickname）
    """
    ranking_id: str
    icon_path: str
    area_id: int
    nickname: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """
        APIレスポンスからUserProfileインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            UserProfileインスタンス
        """
        # APIレスポンスにはranking_nicknameがあり、これをnicknameとして使用
        nickname = data.get('ranking_nickname', '')
        
        # icon_pathがNoneの場合は空文字列に変換
        icon_path = data.get('icon_path', '')
        if icon_path is None:
            icon_path = ''
            
        return cls(
            ranking_id=data.get('ranking_id', ''),  # 実際のレスポンスにはないが互換性のために残す
            icon_path=icon_path,
            area_id=int(data.get('area_id', 0)),  # 実際のレスポンスにはないが互換性のために残す
            nickname=nickname
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        UserProfileインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'ranking_id': self.ranking_id,
            'icon_path': self.icon_path,
            'area_id': self.area_id,
            'nickname': self.nickname
        }


@dataclass
class UserIdentification:
    """
    ユーザー識別情報を表すデータクラス。
    get_id_infoの戻り値に対応します。
    
    Attributes:
        id: ユーザーID
        email: メールアドレス
        name: 名前
        kana: フリガナ
        certified: 認証状態
    """
    id: str
    email: str
    name: str
    kana: str
    certified: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserIdentification':
        """
        APIレスポンスからUserIdentificationインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書
            
        Returns:
            UserIdentificationインスタンス
        """
        # APIレスポンスは {'user': {...}} の形式
        user_data = data.get('user', {})
        if not user_data:
            user_data = data  # userキーがない場合は直接dataを使用
            
        return cls(
            id=str(user_data.get('id', '')),  # intの場合があるのでstrに変換
            email=user_data.get('email', ''),
            name=user_data.get('name', ''),
            kana=user_data.get('kana', ''),
            certified=bool(user_data.get('certified', False))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        UserIdentificationインスタンスを辞書に変換します。
        
        Returns:
            APIレスポンス形式の辞書
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'kana': self.kana,
            'certified': self.certified
        }


@dataclass
class DepositHistoryItem:
    """
    入金履歴の1アイテムを表すデータクラス。
    
    Attributes:
        id: 入金ID
        timestamp: タイムスタンプ
        address: 入金アドレス
        amount: 入金量
        txid: トランザクションID
    """
    id: int
    timestamp: int
    address: str
    amount: Decimal
    txid: str
    
    @property
    def datetime(self):
        """
        UNIXタイムスタンプをdatetimeに変換します。
        
        Returns:
            datetime形式の日時
        """
        from datetime import datetime
        return datetime.fromtimestamp(self.timestamp)


@dataclass
class DepositRecords:
    """
    入金履歴を表すデータクラス。
    
    Attributes:
        items: 入金履歴アイテムのリスト
    """
    items: List[DepositHistoryItem]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DepositRecords':
        """
        APIレスポンスからDepositRecordsインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書（キーが入金ID、値が入金情報）
            
        Returns:
            DepositRecordsインスタンス
        """
        items = []
        for deposit_id, item in data.items():
            if not isinstance(item, dict):
                continue  # 辞書でない項目はスキップ
                
            try:
                deposit_id_int = int(deposit_id)
                timestamp = item.get('timestamp')
                if timestamp is not None and timestamp != '':
                    timestamp = int(timestamp)
                else:
                    timestamp = 0
                    
                items.append(DepositHistoryItem(
                    id=deposit_id_int,
                    timestamp=timestamp,
                    address=item.get('address', ''),
                    amount=Decimal(str(item.get('amount', '0'))),
                    txid=item.get('txid', '')
                ))
            except (ValueError, TypeError, KeyError) as e:
                # 変換エラーが発生した場合はスキップ
                print(f"Warning: Failed to parse deposit item {deposit_id}: {e}")
        return cls(items=items)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        DepositRecordsインスタンスをAPIレスポンス形式のリストに変換します。
        
        Returns:
            APIレスポンス形式のリスト
        """
        return [
            {
                'id': item.id,
                'timestamp': item.timestamp,
                'address': item.address,
                'amount': str(item.amount),
                'txid': item.txid
            }
            for item in self.items
        ]


@dataclass
class WithdrawalHistoryItem:
    """
    出金履歴の1アイテムを表すデータクラス。
    
    Attributes:
        id: 出金ID
        timestamp: タイムスタンプ
        address: 出金アドレス
        amount: 出金量
        txid: トランザクションID
        fee: 手数料
        status: ステータス
    """
    id: int
    timestamp: int
    address: str
    amount: Decimal
    txid: str
    fee: Decimal
    status: str
    
    @property
    def datetime(self):
        """
        UNIXタイムスタンプをdatetimeに変換します。
        
        Returns:
            datetime形式の日時
        """
        from datetime import datetime
        return datetime.fromtimestamp(self.timestamp)


@dataclass
class WithdrawalRecords:
    """
    出金履歴を表すデータクラス。
    
    Attributes:
        items: 出金履歴アイテムのリスト
    """
    items: List[WithdrawalHistoryItem]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WithdrawalRecords':
        """
        APIレスポンスからWithdrawalRecordsインスタンスを作成します。
        
        Args:
            data: APIレスポンスの辞書（キーが出金ID、値が出金情報）
            
        Returns:
            WithdrawalRecordsインスタンス
        """
        items = []
        for withdraw_id, item in data.items():
            if not isinstance(item, dict):
                continue  # 辞書でない項目はスキップ
                
            try:
                withdraw_id_int = int(withdraw_id)
                timestamp = item.get('timestamp')
                if timestamp is not None and timestamp != '':
                    timestamp = int(timestamp)
                else:
                    timestamp = 0
                    
                items.append(WithdrawalHistoryItem(
                    id=withdraw_id_int,
                    timestamp=timestamp,
                    address=item.get('address', ''),
                    amount=Decimal(str(item.get('amount', '0'))),
                    txid=item.get('txid', ''),
                    fee=Decimal(str(item.get('fee', '0'))),
                    status=item.get('status', '')
                ))
            except (ValueError, TypeError, KeyError) as e:
                # 変換エラーが発生した場合はスキップ
                print(f"Warning: Failed to parse withdraw item {withdraw_id}: {e}")
        return cls(items=items)
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        WithdrawalRecordsインスタンスをAPIレスポンス形式のリストに変換します。
        
        Returns:
            APIレスポンス形式のリスト
        """
        return [
            {
                'id': item.id,
                'timestamp': item.timestamp,
                'address': item.address,
                'amount': str(item.amount),
                'txid': item.txid,
                'fee': str(item.fee),
                'status': item.status
            }
            for item in self.items
        ]
