"""Mock classes for testing"""
import asyncio
from trading.kis import KisAPI

class MockKisAPI(KisAPI):
    """테스트용 KIS API"""

    def __init__(self, app_key: str, app_secret: str, account_number: str, account_code: str):
        super().__init__(app_key, app_secret, account_number, account_code)
        self.current_price = 70000  # 모의 가격
        self.balance = 10000000  # 모의 잔고
        self.positions = {}  # 모의 포지션

    async def get_current_price(self, symbol: str) -> float:
        """현재가 조회 - 모의 데이터 반환"""
        await asyncio.sleep(0.01)  # API 호출 시뮬레이션
        return self.current_price

    async def get_balance(self) -> float:
        """계좌 잔고 조회 - 모의 데이터 반환"""
        await asyncio.sleep(0.01)  # API 호출 시뮬레이션
        return self.balance

    async def buy_market(self, symbol: str, quantity: int) -> bool:
        """시장가 매수 - 모의 거래"""
        await asyncio.sleep(0.01)  # API 호출 시뮬레이션
        cost = quantity * self.current_price
        if cost <= self.balance:
            self.balance -= cost
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
            return True
        return False

    async def sell_market(self, symbol: str, quantity: int) -> bool:
        """시장가 매도 - 모의 거래"""
        await asyncio.sleep(0.01)  # API 호출 시뮬레이션
        if symbol in self.positions and self.positions[symbol] >= quantity:
            self.positions[symbol] -= quantity
            self.balance += quantity * self.current_price
            return True
        return False
