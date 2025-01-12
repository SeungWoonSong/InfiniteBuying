"""봇 매니저 모듈"""
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional, List, Type

import aiohttp
import pandas as pd
from dotenv import load_dotenv

from ..schemas.trading import TradeHistory
from .config import BotConfig, TradingConfig
from ..kis.api import KisApi
from .infinite_buying_bot import InfiniteBuyingBot
from .mock_bot import MockInfiniteBuyingBot

logger = logging.getLogger(__name__)

class BotManager:
    """봇 매니저 클래스"""
    _instance = None

    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._bot_config: Optional[BotConfig] = None
            self._trading_config: Optional[TradingConfig] = None
            self._is_running = False
            self._trade_history: List[Dict] = []
            self._task: Optional[asyncio.Task] = None
            
            # 거래 상태
            self._position_count = 0
            self._current_division = 0
            self._average_price = 0
            self._total_investment = 0
            self._current_price = 0
            self._last_trade_time = None
            self._api: Optional[KisApi] = None
            self._bot: Optional[InfiniteBuyingBot] = None
            self._bot_class: Type = InfiniteBuyingBot
            self._test_mode = False

    def set_bot_class(self, bot_class: Type):
        """봇 클래스 설정"""
        self._bot_class = bot_class
        self._test_mode = bot_class == MockInfiniteBuyingBot

    def add_trade_history(self, trade: Dict):
        """거래 내역 추가"""
        self._trade_history.append(trade)

    async def initialize_bot(self, bot_config: BotConfig, trading_config: TradingConfig):
        """봇 초기화"""
        self._bot_config = bot_config
        self._trading_config = trading_config
        
        # KIS API 초기화
        if bot_config.app_key and bot_config.app_secret:
            self._api = KisApi(
                app_key=bot_config.app_key,
                app_secret=bot_config.app_secret,
                account_number=bot_config.account_number,
                account_code=bot_config.account_code,
            )
        
        # 봇 인스턴스 생성
        self._bot = self._bot_class(self._api, bot_config, trading_config)
        
        logger.info("Bot initialized")

    def update_config(self, bot_config: BotConfig, trading_config: TradingConfig):
        """설정 업데이트"""
        asyncio.create_task(self.initialize_bot(bot_config, trading_config))

    async def start(self):
        """봇 시작"""
        if self._is_running:
            raise RuntimeError("Bot is already running")
        
        if not self._bot:
            raise RuntimeError("Bot is not initialized")
        
        self._is_running = True
        logger.info("Bot started")
        
        # 거래 루프 시작
        self._task = asyncio.create_task(self._trading_loop())

    async def stop(self):
        """봇 중지"""
        if not self._is_running:
            raise RuntimeError("Bot is not running")
        
        self._is_running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        if self._bot:
            await self._bot.stop()
        
        logger.info("Bot stopped")

    def reset(self):
        """봇 초기화"""
        if self._is_running:
            asyncio.create_task(self.stop())
        
        self._bot_config = None
        self._trading_config = None
        self._trade_history.clear()
        
        # 거래 상태 초기화
        self._position_count = 0
        self._current_division = 0
        self._average_price = 0
        self._total_investment = 0
        self._current_price = 0
        self._last_trade_time = None
        self._bot = None
        
        logger.info("Bot reset")

    def get_status(self) -> Dict:
        """현재 상태 조회"""
        if not self._bot:
            return {
                "is_running": False,
                "last_update": datetime.now().isoformat(),
                "position_count": 0,
                "current_division": 0,
                "average_price": 0,
                "total_investment": 0,
                "current_price": 0,
                "recent_trades": [],
                "error": "Bot not initialized"
            }
        
        return {
            "is_running": self._is_running,
            "last_update": datetime.now().isoformat(),
            "position_count": self._bot.position_count,
            "current_division": self._bot.current_division,
            "average_price": self._bot.average_price,
            "total_investment": self._bot.total_investment,
            "current_price": self._bot.current_price,
            "recent_trades": self._trade_history[-10:],  # 최근 10개 거래만
            "error": None
        }

    def get_trade_history(self) -> List[Dict]:
        """거래 내역 조회"""
        return self._trade_history

    async def _trading_loop(self):
        """거래 루프"""
        try:
            while self._is_running:
                if self._bot:
                    await self._bot.run_once()
                await asyncio.sleep(self._trading_config.trading_interval)
        except asyncio.CancelledError:
            logger.info("Trading loop cancelled")
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            self._is_running = False
            raise

# 싱글톤 인스턴스
bot_manager = BotManager()
