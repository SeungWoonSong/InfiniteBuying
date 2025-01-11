from typing import Optional
from pykis import PyKis
from .config import BotConfig, TradingConfig
from .trading_bot import InfiniteBuyingBot
import os
from dotenv import load_dotenv
from datetime import datetime

class BotManager:
    _instance = None
    _bot: Optional[InfiniteBuyingBot] = None
    _kis: Optional[PyKis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
        return cls._instance

    async def initialize_bot(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        load_dotenv()
        
        if not self._kis:
            self._kis = PyKis(
                id=os.getenv("ID"),
                account=os.getenv("ACCOUNT"),
                appkey=os.getenv("KIS_APPKEY"),
                secretkey=os.getenv("KIS_SECRETKEY"),
                virtual_id=os.getenv("ID"),
                virtual_appkey=os.getenv("VIRTUAL_KIS_APPKEY"),
                virtual_secretkey=os.getenv("VIRTUAL_KIS_SECRETKEY"),
                keep_token=True,
            )

        if self._bot:
            await self.stop_bot()

        self._bot = InfiniteBuyingBot(self._kis, bot_config, trading_config)
        await self._bot.async_initialize()

    async def start_bot(self):
        """봇 시작"""
        if self._bot:
            await self._bot.run()
            return True
        return False

    async def stop_bot(self):
        """봇 중지"""
        if self._bot:
            await self._bot.stop()
            return True
        return False

    def get_status(self):
        """현재 봇 상태 조회"""
        if not self._bot:
            return None
        
        return {
            "current_price": self._bot.current_price,
            "position_count": self._bot.position_count,
            "average_price": self._bot.average_price,
            "total_investment": self._bot.total_investment,
            "unrealized_pnl": self._bot.unrealized_pnl,
            "current_division": self._bot.current_division,
            "last_updated": datetime.now()
        }

    def get_trade_history(self):
        """거래 내역 조회"""
        if not self._bot:
            return []
        
        return self._bot.trade_history

bot_manager = BotManager()
