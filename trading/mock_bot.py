from trading.infinite_buying_bot import InfiniteBuyingBot
from trading.config import BotConfig, TradingConfig
import asyncio
import random

class MockInfiniteBuyingBot(InfiniteBuyingBot):
    """테스트용 무한매수 봇"""

    def __init__(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        super().__init__(bot_config, trading_config)

    async def _update_market_data(self):
        """시장 데이터 업데이트 (Mock)"""
        self.current_price = random.uniform(60000, 80000)

    async def _execute_first_buy(self):
        """첫 매수 실행 (Mock)"""
        if self.position_count > 0:
            return

        quantity = int(self.trading_config.first_buy_amount / self.current_price)
        if quantity < 1:
            return

        self.position_count = quantity
        self.current_division = 1
        self.average_price = self.current_price
        self.total_investment = self.current_price * quantity

    async def _execute_additional_buy(self):
        """추가 매수 실행 (Mock)"""
        if self.position_count == 0:
            return

        if self.current_division >= self.bot_config.total_divisions:
            return

        if self.current_price >= self.average_price:
            return

        quantity = int(self.trading_config.quantity)
        if quantity < 1:
            return

        self.position_count += quantity
        self.current_division += 1
        self.total_investment += self.current_price * quantity
        self.average_price = self.total_investment / self.position_count

    async def run(self):
        """테스트용 봇 실행"""
        self.is_running = True
        while self.is_running:
            await self._update_market_data()
            await self._execute_first_buy()
            await self._execute_additional_buy()
            await asyncio.sleep(0.01)  # 테스트를 위해 최소 대기 시간 사용
