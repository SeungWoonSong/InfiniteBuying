"""봇 기본 클래스"""
from abc import ABC, abstractmethod
from .config import BotConfig, TradingConfig

class TradingBot(ABC):
    """봇 기본 클래스"""

    def __init__(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        self.bot_config = bot_config
        self.trading_config = trading_config
        self.is_running = False

    @abstractmethod
    async def run(self):
        """봇 실행"""
        pass

    async def stop(self):
        """봇 중지"""
        self.is_running = False
