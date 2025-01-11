"""InfiniteBuyingBot 단위 테스트"""
import unittest
import asyncio
from trading.infinite_buying_bot import InfiniteBuyingBot
from trading.config import BotConfig, TradingConfig

class TestInfiniteBuyingBot(unittest.TestCase):
    """무한매수 봇 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.bot_config = BotConfig(
            symbol="005930",
            total_divisions=10,
            log_dir="logs",
            app_key="test",
            app_secret="test",
            account_number="test",
            account_code="test"
        )
        self.trading_config = TradingConfig(
            initial_amount=1000000,
            single_amount=200000,
            min_order_amount=100000,
            loss_cut_rate=0.03,
            profit_rate=0.02,
            max_buy_times=5,
            trading_interval=1.0
        )
        self.bot = InfiniteBuyingBot(self.bot_config, self.trading_config)

    def test_bot_initialization(self):
        """봇 초기화 테스트"""
        self.assertEqual(self.bot.bot_config, self.bot_config)
        self.assertEqual(self.bot.trading_config, self.trading_config)
        self.assertEqual(self.bot.position_count, 0)
        self.assertEqual(self.bot.current_division, 0)
        self.assertEqual(self.bot.average_price, 0)
        self.assertEqual(self.bot.total_investment, 0)

    def test_market_data_update(self):
        """시장 데이터 업데이트 테스트"""
        async def run_test():
            await self.bot._update_market_data()
            self.assertIsNotNone(self.bot.current_price)
            self.assertGreater(self.bot.current_price, 0)

        asyncio.run(run_test())

    def test_first_buy_execution(self):
        """첫 매수 실행 테스트"""
        async def run_test():
            await self.bot._update_market_data()
            await self.bot._execute_first_buy()
            self.assertGreater(self.bot.position_count, 0)
            self.assertEqual(self.bot.current_division, 1)
            self.assertGreater(self.bot.average_price, 0)
            self.assertGreater(self.bot.total_investment, 0)

        asyncio.run(run_test())

    def test_additional_buy_execution(self):
        """추가 매수 실행 테스트"""
        async def run_test():
            # 첫 매수 실행
            await self.bot._update_market_data()
            await self.bot._execute_first_buy()
            initial_position = self.bot.position_count

            # 추가 매수 실행
            self.bot.current_price = self.bot.average_price * 0.90  # 10% 하락
            additional_quantity = await self.bot._execute_additional_buy()
            self.assertGreater(additional_quantity, 0)
            self.assertEqual(self.bot.current_division, 2)

        asyncio.run(run_test())

    def test_bot_lifecycle(self):
        """봇 생명주기 테스트"""
        async def run_test():
            # 봇 시작
            asyncio.create_task(self.bot.run())
            await asyncio.sleep(0.01)  # 봇이 시작될 때까지 대기
            self.assertTrue(self.bot.is_running)

            # 봇 중지
            await self.bot.stop()
            await asyncio.sleep(0.01)  # 봇이 중지될 때까지 대기
            self.assertFalse(self.bot.is_running)

        asyncio.run(run_test())
