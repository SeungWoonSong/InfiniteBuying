from trading.bot import TradingBot
from trading.kis import KisAPI
from trading.config import BotConfig, TradingConfig
import logging
import asyncio
import os
from datetime import datetime

class InfiniteBuyingBot(TradingBot):
    """무한매수 봇 클래스"""

    def __init__(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        super().__init__(bot_config, trading_config)
        self.position_count = 0
        self.current_division = 0
        self.average_price = 0
        self.total_investment = 0
        self.last_trade_time = None
        self.current_price = None
        self.kis_api = KisAPI(bot_config)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        os.makedirs(self.bot_config.log_dir, exist_ok=True)
        handler = logging.FileHandler(f"{self.bot_config.log_dir}/trading.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        return logger

    async def _update_market_data(self):
        """시장 데이터 업데이트"""
        self.current_price = await self.kis_api.get_current_price(self.bot_config.symbol)
        self.logger.info(f"Current price for {self.bot_config.symbol}: {self.current_price}")

    async def _execute_first_buy(self):
        """첫 매수 실행"""
        if self.position_count > 0:
            return

        quantity = int(self.trading_config.first_buy_amount / self.current_price)
        if quantity < 1:
            self.logger.warning("First buy amount is too small")
            return

        success = await self.kis_api.buy_stock(self.bot_config.symbol, quantity, self.current_price)
        if success:
            self.position_count = quantity
            self.current_division = 1
            self.average_price = self.current_price
            self.total_investment = self.current_price * quantity
            self.last_trade_time = datetime.now()
            self.logger.info(f"First buy executed: {quantity} shares at {self.current_price}")

    async def _execute_additional_buy(self):
        """추가 매수 실행"""
        if self.position_count == 0:
            return

        if self.current_division >= self.bot_config.total_divisions:
            return

        if self.current_price >= self.average_price:
            return

        quantity = int(self.trading_config.quantity)
        if quantity < 1:
            self.logger.warning("Additional buy amount is too small")
            return

        success = await self.kis_api.buy_stock(self.bot_config.symbol, quantity, self.current_price)
        if success:
            self.position_count += quantity
            self.current_division += 1
            self.total_investment += self.current_price * quantity
            self.average_price = self.total_investment / self.position_count
            self.last_trade_time = datetime.now()
            self.logger.info(f"Additional buy executed: {quantity} shares at {self.current_price}")

    async def run(self):
        """봇 실행"""
        self.is_running = True
        self.logger.info("Trading bot started")

        while self.is_running:
            try:
                await self._update_market_data()
                await self._execute_first_buy()
                await self._execute_additional_buy()
                await asyncio.sleep(self.trading_config.trading_interval)
            except Exception as e:
                self.logger.error(f"Error during trading: {e}")
                self.is_running = False

        self.logger.info("Trading bot stopped")

    async def stop(self):
        """봇 중지"""
        self.is_running = False
