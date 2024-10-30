import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
import tempfile

from trading_bot import InfiniteBuyingBot
from config import BotConfig, TradingConfig
from models import TradingState, StockBalance

class MockKisStock:
    def __init__(self, symbol="AAPL", current_price=150.0):
        self.symbol = symbol
        self.current_price = current_price
        self.orders = []
    
    def quote(self):
        return Mock(price=self.current_price)
        
    def buy(self, **kwargs):
        self.orders.append(('buy', kwargs))
        return Mock(order_number='TEST123')
        
    def sell(self, **kwargs):
        self.orders.append(('sell', kwargs))
        return Mock(order_number='TEST123')

class MockKisAccount:
    def __init__(self, balance_data=None):
        self.balance_data = balance_data or {}
    
    def balance(self):
        mock_balance = Mock()
        mock_balance.stocks = []  # 빈 잔고 상태를 나타냄
        
        def stock(symbol):
            return None  # 항상 None 반환하여 주식이 없음을 나타냄
            
        mock_balance.stock = stock
        return mock_balance

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

class TestInfiniteBuyingBot(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
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
        
        # 텔레그램 노티피케이션 모킹
        self.notification_patcher = patch('trading_bot.TelegramNotifier')
        self.mock_notifier = self.notification_patcher.start()
        
        # 스케줄러 모킹
        self.scheduler_patcher = patch('trading_bot.BackgroundScheduler')
        self.mock_scheduler = self.scheduler_patcher.start()

    def tearDown(self):
        """테스트 정리"""
        self.notification_patcher.stop()
        self.scheduler_patcher.stop()

    def test_first_buy(self):
        """첫 매수 테스트"""
        mock_kis = MockKis(current_price=150.0)
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        
        # 첫 매수 실행
        bot.execute_first_buy()
        
        # 주문 확인
        self.assertEqual(len(mock_kis.mock_stock.orders), 1)
        order_type, order_data = mock_kis.mock_stock.orders[0]
        self.assertEqual(order_type, 'buy')
        self.assertEqual(order_data['qty'], 1)
        self.assertEqual(order_data['condition'], 'MOC')

    def test_pre_turn_trading(self):
        """전반전 매매 테스트"""
        mock_kis = MockKis(current_price=150.0)
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        bot.state.turn = 10  # 전반전 상태 설정
        
        # 전반전 매매 실행
        bot._execute_pre_turn_trading(1000)  # $1000 매수
        
        # 주문 확인 (2개의 주문이 있어야 함)
        self.assertEqual(len(mock_kis.mock_stock.orders), 2)
        
        # 0% LOC 매수 확인
        order_type, order_data = mock_kis.mock_stock.orders[0]
        self.assertEqual(order_type, 'buy')
        self.assertEqual(order_data['condition'], 'LOC')
        
        # (10-T/2)% LOC 매수 확인
        order_type, order_data = mock_kis.mock_stock.orders[1]
        self.assertEqual(order_type, 'buy')
        self.assertEqual(order_data['condition'], 'LOC')

    def test_post_turn_trading(self):
        """후반전 매매 테스트"""
        mock_kis = MockKis(current_price=150.0)
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        bot.state.turn = 25  # 후반전 상태 설정
        
        # 후반전 매매 실행
        bot._execute_post_turn_trading(1000)  # $1000 매수
        
        # 주문 확인
        self.assertEqual(len(mock_kis.mock_stock.orders), 1)
        order_type, order_data = mock_kis.mock_stock.orders[0]
        self.assertEqual(order_type, 'buy')
        self.assertEqual(order_data['condition'], 'LOC')

    def test_sell_orders(self):
        """매도 주문 테스트"""
        mock_kis = MockKis(current_price=150.0)
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        
        # 테스트용 잔고 생성
        balance = StockBalance(
            quantity=Decimal('100'),
            average_price=140.0,
            current_price=150.0
        )
        
        # 매도 주문 실행
        bot._execute_sell_orders(balance)
        
        # 주문 확인 (2개의 매도 주문)
        self.assertEqual(len(mock_kis.mock_stock.orders), 2)
        
        # 1/4 LOC 매도 확인
        order_type, order_data = mock_kis.mock_stock.orders[0]
        self.assertEqual(order_type, 'sell')
        self.assertEqual(order_data['qty'], 25)  # 100의 1/4
        self.assertEqual(order_data['condition'], 'LOC')
        
        # 3/4 지정가 매도 확인
        order_type, order_data = mock_kis.mock_stock.orders[1]
        self.assertEqual(order_type, 'sell')
        self.assertEqual(order_data['qty'], 75)  # 100의 3/4

    def test_quarter_stop_loss(self):
        """쿼터손절 테스트"""
        mock_kis = MockKis(current_price=150.0)
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        bot.state.turn = 39.5  # 쿼터손절 상태
        
        # 테스트용 잔고 생성
        balance = StockBalance(
            quantity=Decimal('100'),
            average_price=140.0,
            current_price=150.0
        )
        
        # 쿼터손절 실행
        bot._execute_quarter_stop_loss(balance)
        
        # 주문 확인
        self.assertEqual(len(mock_kis.mock_stock.orders), 1)
        order_type, order_data = mock_kis.mock_stock.orders[0]
        self.assertEqual(order_type, 'sell')
        self.assertEqual(order_data['qty'], 25)  # 100의 1/4
        self.assertEqual(order_data['condition'], 'MOC')

    def test_cycle_completion(self):
        """사이클 완료 테스트"""
        mock_kis = MockKis()
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        
        # get_balance가 None을 반환하도록 설정
        def mock_get_balance():
            return None
        
        bot.get_balance = mock_get_balance
        
        # 사이클 완료 체크
        is_completed = bot.check_cycle_completion()
        
        self.assertTrue(is_completed)
        self.assertEqual(bot.state.turn, 0)
        self.assertTrue(bot.state.is_first_buy)

    def test_calculate_buy_quantity(self):
        """매수 수량 계산 테스트"""
        mock_kis = MockKis()
        bot = InfiniteBuyingBot(mock_kis, self.config, self.trading_config)
        
        # 테스트 케이스
        test_cases = [
            (1000, 150.0, 6),    # $1000/$150 = 6.66... -> 6주
            (1000, 50.0, 20),    # $1000/$50 = 20주
            (100, 150.0, 0),     # $100/$150 = 0.66... -> 0주
            (1500, 149.99, 10)   # $1500/$149.99 = 10.00... -> 10주
        ]
        
        for amount, price, expected in test_cases:
            qty = bot.calculate_buy_quantity(amount, price)
            self.assertEqual(qty, expected)

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()