import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asynctest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
import tempfile
import asyncio

from trading_bot import InfiniteBuyingBot
from config import BotConfig, TradingConfig
from models import TradingState, StockBalance, OrderTracking

class MockKisStock:
    def __init__(self, symbol="AAPL", current_price=150.0):
        self.symbol = symbol
        self.current_price = current_price
        self.orders = []
        
    def quote(self):
        return Mock(price=self.current_price)
        
    # 동기 함수로 변경하고 promise pattern 사용
    def buy(self, **kwargs):
        order = AsyncMock()
        order.number = f'BUY_{len(self.orders)}'
        order.symbol = self.symbol
        order.type = 'buy'
        order.price = kwargs.get('price', self.current_price)
        order.qty = kwargs.get('qty')
        order.condition = kwargs.get('condition')
        order.executed_qty = kwargs.get('qty')
        
        self.orders.append(('buy', kwargs, order))
        
        # Promise pattern으로 반환
        future = asyncio.Future()
        future.set_result(order)
        return future

    def sell(self, **kwargs):
        order = AsyncMock()
        order.number = f'SELL_{len(self.orders)}'
        order.symbol = self.symbol
        order.type = 'sell'
        order.price = kwargs.get('price', self.current_price)
        order.qty = kwargs.get('qty')
        order.condition = kwargs.get('condition')
        order.executed_qty = kwargs.get('qty')

        self.orders.append(('sell', kwargs, order))
        
        # Promise pattern으로 반환
        future = asyncio.Future()
        future.set_result(order)
        return future

class MockKisAccount:
    def __init__(self, balance_data=None):
        self.balance_data = balance_data or {}
        self.deposits = {'USD': Mock(amount=10000)}
    
    def balance(self):
        mock_balance = Mock()
        mock_balance.stocks = []
        mock_balance.deposits = self.deposits
        
        def stock(symbol):
            return None
            
        mock_balance.stock = stock
        return mock_balance

    async def pending_orders(self):
        # 주문이 바로 체결된 것처럼 빈 dict 반환
        return {}

class MockKis:
    def __init__(self, symbol="AAPL", current_price=150.0):
        self.mock_stock = MockKisStock(symbol, current_price)
        self.mock_account = MockKisAccount()
    
    def stock(self, symbol):
        return self.mock_stock
        
    def account(self):
        return self.mock_account
        
    def trading_hours(self, market):
        return Mock(close_kst="05:00:00")

class TestInfiniteBuyingBot(asynctest.TestCase):
    def setUp(self):
        """동기 초기화"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = BotConfig(
            symbol="AAPL",
            total_divisions=40,
            log_dir=Path(self.temp_dir)
        )
        self.trading_config = TradingConfig(
            first_buy_amount=1,
            pre_turn_threshold=20,
            quarter_loss_start=39
        )
        
        # Mocking
        self.notification_patcher = patch('trading_bot.TelegramNotifier')
        mock_notifier_class = self.notification_patcher.start()
        self.mock_notifier = AsyncMock()
        mock_notifier_class.return_value = self.mock_notifier
        
        self.scheduler_patcher = patch('trading_bot.AsyncIOScheduler')
        self.mock_scheduler = self.scheduler_patcher.start()
        
        # Create mock KIS
        self.mock_kis = MockKis()
        
        # Create bot instance
        self.bot = InfiniteBuyingBot(
            self.mock_kis,
            self.config,
            self.trading_config
        )
        
        # Mock track_order
        self.bot.track_order = AsyncMock(return_value=True)

    async def asyncSetUp(self):
        """비동기 초기화"""
        await super().asyncSetUp()
        # 필요한 추가 비동기 초기화 작업

class TestInfiniteBuyingBot(asynctest.TestCase):
    def setUp(self):
        """동기 초기화"""
        print("\n=== Test Setup ===")
        self.temp_dir = tempfile.mkdtemp()
        self.config = BotConfig(
            symbol="AAPL",
            total_divisions=40,
            log_dir=Path(self.temp_dir)
        )
        self.trading_config = TradingConfig(
            first_buy_amount=1,
            pre_turn_threshold=20,
            quarter_loss_start=39
        )
        
        # Mocking setup...
        self.notification_patcher = patch('trading_bot.TelegramNotifier')
        mock_notifier_class = self.notification_patcher.start()
        self.mock_notifier = AsyncMock()
        mock_notifier_class.return_value = self.mock_notifier
        
        self.scheduler_patcher = patch('trading_bot.AsyncIOScheduler')
        self.mock_scheduler = self.scheduler_patcher.start()
        
        # Create mock KIS and bot
        self.mock_kis = MockKis()
        self.bot = InfiniteBuyingBot(
            self.mock_kis,
            self.config,
            self.trading_config
        )
        self.bot.track_order = AsyncMock(return_value=True)
        print("Setup completed successfully")

    async def test_first_buy(self):
        """첫 매수 테스트"""
        print("\n=== Testing First Buy ===")
        self.mock_kis.mock_stock.orders = []
        
        await self.bot.execute_first_buy()
        
        orders = self.mock_kis.mock_stock.orders
        print(f"Number of orders placed: {len(orders)}")
        if orders:
            order_type, kwargs, _ = orders[0]
            print(f"Order type: {order_type}")
            print(f"Quantity: {kwargs.get('qty')}")
            print(f"Condition: {kwargs.get('condition')}")
            
            self.assertEqual(len(orders), 1, "Should place exactly one order")
            self.assertEqual(order_type, 'buy', "Should be a buy order")
            self.assertEqual(kwargs['qty'], self.trading_config.first_buy_amount, "Quantity should match first buy amount")
            self.assertEqual(kwargs['condition'], 'MOC', "Should be a MOC order")
        print("First buy test completed successfully")

    async def test_pre_turn_trading(self):
        """전반전 매매 테스트"""
        print("\n=== Testing Pre-Turn Trading ===")
        self.mock_kis.mock_stock.orders = []
        self.bot.state.turn = 10
        
        await self.bot._execute_pre_turn_trading(1000)

        orders = self.mock_kis.mock_stock.orders
        print(f"Number of orders placed: {len(orders)}")
        for i, (order_type, kwargs, _) in enumerate(orders, 1):
            print(f"\nOrder {i}:")
            print(f"Type: {order_type}")
            print(f"Quantity: {kwargs.get('qty')}")
            print(f"Condition: {kwargs.get('condition')}")
            print(f"Price: {kwargs.get('price')}")
        
        self.assertEqual(len(orders), 2, "Should place exactly two orders")
        self.assertEqual(orders[0][0], 'buy', "First should be a buy order")
        self.assertEqual(orders[0][1]['condition'], 'LOC', "First should be a LOC order")
        self.assertEqual(orders[1][0], 'buy', "Second should be a buy order")
        self.assertEqual(orders[1][1]['condition'], 'LOC', "Second should be a LOC order")
        print("Pre-turn trading test completed successfully")

    async def test_quarter_stop_loss(self):
        """쿼터손절 테스트"""
        print("\n=== Testing Quarter Stop Loss ===")
        self.mock_kis.mock_stock.orders = []
        balance = StockBalance(
            quantity=Decimal('100'),
            average_price=140.0,
            current_price=150.0
        )
        
        print(f"Initial balance: {balance.quantity} shares @ ${balance.average_price}")
        await self.bot._execute_quarter_stop_loss(balance)

        orders = self.mock_kis.mock_stock.orders
        print(f"Number of orders placed: {len(orders)}")
        if orders:
            order_type, kwargs, _ = orders[0]
            print(f"Order type: {order_type}")
            print(f"Quantity: {kwargs.get('qty')}")
            print(f"Condition: {kwargs.get('condition')}")
            
            self.assertEqual(len(orders), 1, "Should place exactly one order")
            self.assertEqual(order_type, 'sell', "Should be a sell order")
            self.assertEqual(kwargs['qty'], 25, "Should sell quarter of position")
            self.assertEqual(kwargs['condition'], 'MOC', "Should be a MOC order")
        print("Quarter stop loss test completed successfully")

    async def test_sell_orders(self):
        """매도 주문 테스트"""
        print("\n=== Testing Sell Orders ===")
        self.mock_kis.mock_stock.orders = []
        self.bot.state.turn = 10
        balance = StockBalance(
            quantity=Decimal('100'),
            average_price=140.0,
            current_price=150.0
        )
        
        print(f"Initial balance: {balance.quantity} shares @ ${balance.average_price}")
        await self.bot._execute_sell_orders(balance)

        orders = self.mock_kis.mock_stock.orders
        print(f"Number of orders placed: {len(orders)}")
        for i, (order_type, kwargs, _) in enumerate(orders, 1):
            print(f"\nOrder {i}:")
            print(f"Type: {order_type}")
            print(f"Quantity: {kwargs.get('qty')}")
            print(f"Condition: {kwargs.get('condition')}")
            print(f"Price: {kwargs.get('price')}")
        
        self.assertEqual(len(orders), 2, "Should place exactly two sell orders")
        self.assertEqual(orders[0][0], 'sell', "First should be a sell order")
        self.assertEqual(orders[0][1]['condition'], 'LOC', "First should be a LOC order")
        self.assertEqual(orders[1][0], 'sell', "Second should be a sell order")
        print("Sell orders test completed successfully")

    def tearDown(self):
        """테스트 정리"""
        print("\n=== Test Cleanup ===")
        try:
            if hasattr(self, 'notification_patcher'):
                self.notification_patcher.stop()
            if hasattr(self, 'scheduler_patcher'):
                self.scheduler_patcher.stop()
            print("Cleanup completed successfully")
        except Exception as e:
            print(f"Error in cleanup: {e}")

if __name__ == '__main__':
    print("\n=== Starting Trading Bot Tests ===\n")
    asynctest.main(verbosity=2)
