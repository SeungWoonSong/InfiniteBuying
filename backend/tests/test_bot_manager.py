import unittest
import asyncio
from trading.bot_manager import BotManager
from trading.config import BotConfig, TradingConfig
from trading.mock_bot import MockInfiniteBuyingBot

class TestBotManager(unittest.TestCase):
    """봇 관리자 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.bot_manager = BotManager()
        self.bot_manager.set_bot_class(MockInfiniteBuyingBot)

    def test_singleton(self):
        """BotManager가 싱글톤 패턴을 따르는지 테스트"""
        another_manager = BotManager()
        self.assertEqual(id(self.bot_manager), id(another_manager))

    def test_trade_history_management(self):
        """거래 내역 관리 기능 테스트"""
        # 거래 내역 추가
        trade = {
            "symbol": "005930",
            "price": 70000,
            "quantity": 10,
            "type": "buy"
        }
        self.bot_manager.add_trade_history(trade)

        # 거래 내역 조회
        history = self.bot_manager.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], trade)

        # 거래 내역 초기화
        self.bot_manager.reset()
        history = self.bot_manager.get_trade_history()
        self.assertEqual(len(history), 0)

    def test_bot_lifecycle(self):
        """봇 생명주기 관리 테스트"""
        async def run_lifecycle_test():
            # 봇 초기화
            bot_config = BotConfig(
                symbol="005930",
                total_divisions=10,
                log_dir="logs",
                app_key="test",
                app_secret="test",
                account_number="test",
                account_code="test"
            )
            trading_config = TradingConfig(
                stock_code="005930",
                target_price=70000,
                quantity=10,
                first_buy_amount=1000000,
                pre_turn_threshold=20,
                quarter_loss_start=39,
                trading_interval=1,
                max_trades_per_day=10,
                use_real_trading=False
            )
            await self.bot_manager.initialize_bot(bot_config, trading_config)

            # 봇 시작
            await self.bot_manager.start()
            await asyncio.sleep(0.01)  # 봇이 시작될 때까지 대기
            self.assertTrue(self.bot_manager.get_status())

            # 봇 중지
            await self.bot_manager.stop()
            await asyncio.sleep(0.01)  # 봇이 중지될 때까지 대기
            self.assertFalse(self.bot_manager.get_status())

        asyncio.run(run_lifecycle_test())

if __name__ == '__main__':
    unittest.main()
