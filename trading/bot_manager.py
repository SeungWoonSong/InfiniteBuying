from typing import Type, List, Dict, Optional
from datetime import datetime
import logging
import os
from tests.mocks.mock_bot import MockInfiniteBuyingBot
from trading.infinite_buying_bot import InfiniteBuyingBot
from trading.config import BotConfig, TradingConfig
import asyncio

class BotManager:
    """봇 관리자"""
    _instance = None
    _bot = None
    _bot_class = MockInfiniteBuyingBot
    _trade_history: List[Dict] = []

    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_bot_class(cls, bot_class: Type[InfiniteBuyingBot]):
        """봇 클래스 설정"""
        cls._bot_class = bot_class

    @classmethod
    def reset(cls):
        """봇 초기화"""
        cls._bot = None
        cls._trade_history = []

    @classmethod
    def get_trade_history(cls) -> List[Dict]:
        """거래 내역 조회"""
        return cls._trade_history

    @classmethod
    def add_trade_history(cls, trade: Dict):
        """거래 내역 추가"""
        cls._trade_history.append(trade)

    @classmethod
    async def initialize_bot(cls, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        if cls._bot is not None:
            await cls.stop()
        cls._bot = cls._bot_class(bot_config=bot_config, trading_config=trading_config)

    @classmethod
    async def start(cls):
        """봇 시작"""
        if cls._bot is None:
            raise ValueError("Bot not initialized")
        asyncio.create_task(cls._bot.run())

    @classmethod
    async def stop(cls):
        """봇 중지"""
        if cls._bot is not None:
            await cls._bot.stop()

    @classmethod
    def get_status(cls) -> bool:
        """봇 상태 조회"""
        if cls._bot is None:
            return False
        return cls._bot.is_running

bot_manager = BotManager()
