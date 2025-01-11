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
        self.bot_manager.add_trade(trade)

        # 거래 내역 확인
        history = self.bot_manager.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["symbol"], "005930")
        self.assertEqual(history[0]["action"], "BUY")

        # 거래 내역 파일 저장 확인
        self.assertTrue(self.test_history_file.exists())
        saved_history = json.loads(self.test_history_file.read_text())
        self.assertEqual(len(saved_history), 1)

    async def test_bot_lifecycle(self):
        """봇 생명주기 관리 테스트"""
        # 봇 초기화
        bot_config = BotConfig(
            symbol="005930",
            total_divisions=40,
            log_dir=Path("logs")
        )
        trading_config = TradingConfig(
            first_buy_amount=1,
            pre_turn_threshold=20,
            quarter_loss_start=39
        )
        await self.bot_manager.initialize_bot(bot_config, trading_config)

        # 봇 시작
        result = await self.bot_manager.start()
        self.assertTrue(result)
        status = self.bot_manager.get_status()
        self.assertIsNotNone(status)

        # 봇 중지
        result = await self.bot_manager.stop()
        self.assertTrue(result)

        # 봇 초기화
        result = await self.bot_manager.reset()
        self.assertTrue(result)
        history = self.bot_manager.get_trade_history()
        self.assertEqual(len(history), 0)

def run_async_test(test_case, coroutine):
    """비동기 테스트 실행 헬퍼 함수"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)

if __name__ == '__main__':
    unittest.main()
