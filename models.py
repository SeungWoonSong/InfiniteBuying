# models.py
from dataclasses import dataclass, asdict
from decimal import Decimal
from datetime import datetime

@dataclass
class TradingState:
    """매매 상태"""
    cycle_number: int = 1          # 현재 사이클 번호
    turn: float = 0                # 현재 회차
    initial_price: float = 0       # 첫 매수 가격
    total_investment: float = 0    # 총 투자금
    is_first_buy: bool = True      # 첫 매수 여부
    last_updated: datetime = None  # 마지막 업데이트 시간
    
    def reset(self):
        """새로운 사이클 시작을 위한 초기화"""
        self.turn = 0
        self.initial_price = 0
        self.is_first_buy = True
        self.cycle_number += 1
        self.last_updated = datetime.now()

    def to_dict(self):
        """객체를 딕셔너리로 변환, JSON 직렬화 가능하게 변환"""
        data = asdict(self)
        # datetime 객체를 문자열로 변환
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        """딕셔너리를 객체로 변환"""
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

@dataclass
class StockBalance:
    """주식 잔고 정보"""
    quantity: Decimal      # 보유 수량
    average_price: float  # 평균 단가
    current_price: float  # 현재가
    
    @property
    def total_value(self) -> float:
        """총 평가금액"""
        return float(self.quantity) * self.current_price

    @property
    def profit_rate(self) -> float:
        """수익률"""
        return (self.current_price - self.average_price) / self.average_price * 100

@dataclass
class OrderTracking:
    order_number: str  # 주문번호
    symbol: str       # 종목코드
    type: str        # 매수/매도
    price: float     # 주문가격 
    qty: int         # 주문수량
    executed_qty: int # 체결수량
    condition: str    # 주문조건
    time: datetime   # 주문시각

    @property
    def pending_qty(self) -> int:
        """미체결 수량"""
        return self.qty - self.executed_qty

    @property 
    def is_complete(self) -> bool:
        """체결 완료 여부"""
        return self.executed_qty == self.qty