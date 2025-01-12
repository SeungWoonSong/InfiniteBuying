from typing import Optional
from .config import BotConfig

class KisAPI:
    """한국투자증권 API 클래스"""

    def __init__(self, bot_config: BotConfig):
        """API 초기화"""
        self.bot_config = bot_config
        self.test_mode = True

    async def get_current_price(self, symbol: str) -> float:
        """현재가 조회"""
        if self.test_mode:
            return 70000.0
        
        # TODO: 실제 API 호출
        raise NotImplementedError

    async def buy_stock(self, symbol: str, quantity: int, price: float) -> bool:
        """주식 매수"""
        if self.test_mode:
            return True
        
        # TODO: 실제 API 호출
        raise NotImplementedError

    async def sell_stock(self, symbol: str, quantity: int, price: float) -> bool:
        """주식 매도"""
        if self.test_mode:
            return True
        
        # TODO: 실제 API 호출
        raise NotImplementedError
