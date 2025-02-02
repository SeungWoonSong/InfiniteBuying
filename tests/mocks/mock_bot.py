"""Mock classes for testing"""
from backend.app.trading.infinite_buying_bot import InfiniteBuyingBot
from backend.app.trading.config import BotConfig, TradingConfig
import asyncio

class MockInfiniteBuyingBot(InfiniteBuyingBot):
    """테스트용 무한매수 봇"""

    def __init__(self, bot_config: BotConfig, trading_config: TradingConfig):
        super().__init__(bot_config, trading_config)
        self.current_price = 70000  # 삼성전자 시가
        self.position_count = 0
        self.total_investment = 0
        self.average_price = 0
        self.current_division = 0

    async def _update_market_data(self):
        """시장 데이터 업데이트 - 모의 데이터 사용"""
        await asyncio.sleep(0.01)  # 실제 API 호출 시뮬레이션

    async def _execute_first_buy(self):
        """첫 매수 실행 - 모의 거래"""
        if self.position_count == 0:
            quantity = int(self.trading_config.single_amount / self.current_price)
            self.position_count = quantity
            self.total_investment = quantity * self.current_price
            self.average_price = self.current_price
            self.current_division = 1
            self.logger.info(f"First buy executed: {quantity} shares at {self.current_price}")

    async def _execute_additional_buy(self):
        """추가 매수 실행 - 모의 거래"""
        if not self.position_count > 0:
            return 0

        if self.current_division >= self.bot_config.total_divisions:
            return 0

        if self.current_price >= self.average_price:
            return 0

        drop_rate = (self.average_price - self.current_price) / self.average_price
        if drop_rate > 0.05:  # 5% 이상 하락 시 추가 매수
            quantity = int(self.trading_config.single_amount / self.current_price)
            if quantity > 0:
                self.position_count += quantity
                self.total_investment += quantity * self.current_price
                self.current_division += 1
                self.average_price = self.total_investment / self.position_count
                self.logger.info(f"Additional buy executed: {quantity} shares at {self.current_price}")
                return quantity
        return 0

    async def run(self):
        """테스트용 봇 실행"""
        self.is_running = True
        while self.is_running:
            await self._update_market_data()
            await self._execute_first_buy()
            await self._execute_additional_buy()
            await asyncio.sleep(0.01)  # 테스트를 위해 최소 대기 시간 사용
