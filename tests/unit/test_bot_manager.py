import unittest
import asyncio
import json
from pathlib import Path
from trading.bot_manager import BotManager
from trading.config import BotConfig, TradingConfig

class TestBotManager(unittest.TestCase):
    def setUp(self):
        self.bot_manager = BotManager()
        self.test_history_file = Path("trading/trade_history.json")
        if self.test_history_file.exists():
            self.test_history_file.unlink()

    def tearDown(self):
        if self.test_history_file.exists():
            self.test_history_file.unlink()

    def test_singleton(self):
        """BotManager가 싱글톤 패턴을 따르는지 테스트"""
        another_manager = BotManager()
        self.assertEqual(id(self.bot_manager), id(another_manager))

    def test_trade_history_management(self):
        """거래 내역 관리 기능 테스트"""
        # 새로운 거래 추가
        trade = {
            "symbol": "005930",
            "action": "BUY",
            "price": 70000,
            "quantity": 10,
            "division": 1,
            "total_amount": 700000
        }
        self.bot_manager.add_trade_history(trade)

        # 거래 내역 확인
        history = self.bot_manager.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["symbol"], "005930")
        self.assertEqual(history[0]["action"], "BUY")

    async def test_bot_lifecycle(self):
        """봇 생명주기 관리 테스트"""
        # 봇 초기화
        bot_config = BotConfig(
            symbol="005930",
            total_divisions=5,
            log_dir="logs",
            app_key="test_app_key",
            app_secret="test_app_secret",
            account_number="test_account",
            account_code="01"
        )
        trading_config = TradingConfig(
            initial_amount=1000000,
            single_amount=200000,
            min_order_amount=100000,
            loss_cut_rate=0.03,
            profit_rate=0.02,
            max_buy_times=5,
            trading_interval=1.0
        )

        # 봇 초기화
        await self.bot_manager.initialize_bot(bot_config, trading_config)
        self.assertIsNotNone(self.bot_manager._bot)

        # 봇 시작
        await self.bot_manager.start()
        self.assertTrue(self.bot_manager.is_running())

        # 봇 중지
        await self.bot_manager.stop()
        self.assertFalse(self.bot_manager.is_running())

def run_async_test(test_case, coroutine):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutine)

if __name__ == '__main__':
    unittest.main()
