from pykis import PyKis
from .config import BotConfig, TradingConfig
import logging
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

class TradingBot(ABC):
    """트레이딩 봇 기본 클래스"""

    @abstractmethod
    def __init__(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        pass

    @abstractmethod
    async def run(self):
        """봇 실행"""
        pass

    @abstractmethod
    async def stop(self):
        """봇 중지"""
        pass


class InfiniteBuyingBot(TradingBot):
    def __init__(self, kis: PyKis, bot_config: BotConfig, trading_config: TradingConfig):
        super().__init__(bot_config, trading_config)
        self.kis = kis
        self.trades_today = 0
        self.last_trade_time = None
        self.is_running = False
        self._setup_logging()

    def _setup_logging(self):
        """로깅 설정"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 파일 핸들러
        fh = logging.FileHandler('logs/trading.log')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # 콘솔 핸들러
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    async def run(self):
        """트레이딩 시작"""
        self.is_running = True
        self.logger.info("Trading bot started")
        
        while self.is_running:
            try:
                await self._trade_cycle()
            except Exception as e:
                self.logger.error(f"Error during trading cycle: {str(e)}")
            
            await asyncio.sleep(self.trading_config.trading_interval)

    async def stop(self):
        """트레이딩 중지"""
        self.is_running = False
        self.logger.info("Trading bot stopped")

    async def _trade_cycle(self):
        """한 번의 트레이딩 사이클 실행"""
        # 오늘 거래 횟수 체크
        if self.trades_today >= self.trading_config.max_trades_per_day:
            self.logger.info("Maximum trades for today reached")
            return

        # 현재가 확인
        current_price = await self._get_current_price()
        
        # 목표가 도달 시 매수
        if current_price <= self.trading_config.target_price:
            await self._execute_buy()
            self.trades_today += 1
            self.last_trade_time = datetime.now()

    async def _get_current_price(self) -> float:
        """현재가 조회"""
        # TODO: PyKis를 사용하여 현재가 조회 구현
        return 0.0

    async def _execute_buy(self):
        """매수 주문 실행"""
        # TODO: PyKis를 사용하여 매수 주문 구현
        self.logger.info(f"Buy order executed: {self.trading_config.quantity} shares at market price")
