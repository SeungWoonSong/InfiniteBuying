import sys
import os
import unittest
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot import InfiniteBuyingBot
from config import BotConfig, TradingConfig
from models import TradingState, StockBalance

class MockKisAccount:
    def __init__(self, deposits, stocks):
        self.deposits = deposits
        self.stocks = stocks
    
    def balance(self):
        mock_balance = Mock()
        mock_balance.deposits = self.deposits
        mock_balance.stocks = self.stocks
        
        # stock 메서드 구현
        def stock(symbol):
            return next((s for s in self.stocks if s.symbol == symbol), None)
        mock_balance.stock = stock
        
        return mock_balance

class TestTQQQOrderCalculations(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = BotConfig(
            symbol="TQQQ",
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
        
        # PyKis 인스턴스 생성
        self.kis = self.create_mock_kis()
        
        # 봇 인스턴스 생성
        self.bot = InfiniteBuyingBot(self.kis, self.config, self.trading_config)

    def tearDown(self):
        """테스트 정리"""
        self.notification_patcher.stop()
        self.scheduler_patcher.stop()

    def create_mock_kis(self):
        """Mock PyKis 인스턴스 생성"""
        mock_kis = Mock()
        
        # TQQQ의 현재 시세 데이터 설정
        mock_quote = Mock()
        mock_quote.price = 45.67  # TQQQ의 현재 가격
        
        mock_stock = Mock()
        mock_stock.symbol = "TQQQ"
        mock_stock.quote.return_value = mock_quote
        
        # 계좌 잔고 설정
        mock_deposits = {
            'USD': Mock(amount=10000.00)  # $10,000 예수금
        }
        mock_stocks = [
            Mock(
                symbol="TQQQ",
                qty=Decimal('20'),  # 20주 보유
                price=43.50,        # 평균단가 $43.50
                amount=870.00       # 총 매수금액
            )
        ]
        
        mock_account = MockKisAccount(mock_deposits, mock_stocks)
        mock_kis.account = lambda: mock_account
        mock_kis.stock = lambda x: mock_stock
        
        return mock_kis

    def test_account_status(self):
        """계좌 상태 출력"""
        balance = self.kis.account().balance()
        deposits = balance.deposits['USD'].amount
        stock = balance.stock("TQQQ")
        quote = self.kis.stock("TQQQ").quote()
        
        print(f"\n=== 계좌 상태 ===")
        print(f"예수금: ${deposits:,.2f}")
        print(f"TQQQ 현재가: ${quote.price:.2f}")
        if stock:
            print(f"보유수량: {stock.qty}주")
            print(f"평균단가: ${stock.price:.2f}")
            print(f"총 매수금액: ${stock.amount:.2f}")
            current_value = float(stock.qty) * quote.price
            profit_rate = (quote.price - stock.price) / stock.price * 100
            print(f"평가금액: ${current_value:,.2f}")
            print(f"수익률: {profit_rate:.2f}%")
        print(f"총 자산: ${(deposits + (stock.amount if stock else 0)):,.2f}")

    def test_calculate_first_buy(self):
        """첫 매수 테스트"""
        quote = self.kis.stock("TQQQ").quote()
        balance = self.kis.account().balance()
        deposits = balance.deposits['USD'].amount
        
        amount = quote.price * self.trading_config.first_buy_amount
        
        print(f"\n=== 첫 매수 테스트 ===")
        print(f"예수금: ${deposits:,.2f}")
        print(f"TQQQ 현재가: ${quote.price:.2f}")
        print(f"매수 수량: {self.trading_config.first_buy_amount}주")
        print(f"필요 금액: ${amount:.2f}")
        print(f"매수 가능 여부: {'가능' if deposits >= amount else '불가능'}")

    def test_calculate_pre_turn_buy(self):
        """전반전 매수 테스트"""
        balance = self.kis.account().balance()
        deposits = balance.deposits['USD'].amount
        quote = self.kis.stock("TQQQ").quote()
        current_price = quote.price
        
        # 테스트할 회차
        test_turns = [1, 5, 10, 15, 19]
        
        # 잔여 투자금액 계산
        total_investment = deposits * 0.9  # 예수금의 90%를 총 투자금액으로 설정
        
        print(f"\n=== 전반전 매수 테스트 ===")
        print(f"예수금: ${deposits:,.2f}")
        print(f"총 투자금액: ${total_investment:,.2f}")
        print(f"TQQQ 현재가: ${current_price:.2f}")
        
        for turn in test_turns:
            self.bot.state.turn = turn
            percent = 10 - (turn/2)
            
            # 남은 회차 수 계산
            remaining_turns = self.config.total_divisions - turn
            # 회차당 투자금액 계산
            amount_per_turn = total_investment / remaining_turns
            
            print(f"\n[{turn}회차 - {percent:.1f}% LOC]")
            print(f"회차당 투자금액: ${amount_per_turn:,.2f}")
            
            loc_price = current_price * (1 + percent/100)
            half_amount = amount_per_turn / 2
            
            # 0% LOC 수량
            qty1 = self.bot.calculate_buy_quantity(half_amount, current_price)
            # (10-T/2)% LOC 수량
            qty2 = self.bot.calculate_buy_quantity(half_amount, loc_price)
            
            total_qty = qty1 + qty2
            total_amount = (qty1 * current_price) + (qty2 * loc_price)
            
            print(f"0% LOC: {qty1}주 (${qty1*current_price:.2f})")
            print(f"{percent:.1f}% LOC: {qty2}주 (${qty2*loc_price:.2f})")
            print(f"총 {total_qty}주 (${total_amount:.2f})")

    def test_calculate_post_turn_buy(self):
        """후반전 매수 테스트"""
        balance = self.kis.account().balance()
        deposits = balance.deposits['USD'].amount
        quote = self.kis.stock("TQQQ").quote()
        current_price = quote.price
        
        # 테스트할 회차
        test_turns = [20, 25, 30, 35, 38]
        
        # 잔여 투자금액 계산
        total_investment = deposits * 0.9  # 예수금의 90%를 총 투자금액으로 설정
        
        print(f"\n=== 후반전 매수 테스트 ===")
        print(f"예수금: ${deposits:,.2f}")
        print(f"총 투자금액: ${total_investment:,.2f}")
        print(f"TQQQ 현재가: ${current_price:.2f}")
        
        for turn in test_turns:
            self.bot.state.turn = turn
            percent = 10 - (turn/2)
            
            # 남은 회차 수 계산
            remaining_turns = self.config.total_divisions - turn
            # 회차당 투자금액 계산
            amount_per_turn = total_investment / remaining_turns
            
            print(f"\n[{turn}회차 - {percent:.1f}% LOC]")
            print(f"회차당 투자금액: ${amount_per_turn:,.2f}")
            
            loc_price = current_price * (1 + percent/100)
            qty = self.bot.calculate_buy_quantity(amount_per_turn, loc_price)
            total_amount = qty * loc_price
            
            print(f"매수 수량: {qty}주")
            print(f"매수 금액: ${total_amount:.2f}")

    def test_calculate_quarter_loss(self):
        """쿼터손절 테스트"""
        balance = self.kis.account().balance()
        stock = balance.stock("TQQQ")
        quote = self.kis.stock("TQQQ").quote()
        
        print(f"\n=== 쿼터손절 테스트 ===")
        if stock:
            current_value = float(stock.qty) * quote.price
            quarter_qty = int(stock.qty) // 4
            expected_amount = quarter_qty * quote.price
            
            print(f"보유수량: {stock.qty}주 (${current_value:,.2f})")
            print(f"쿼터손절 수량: {quarter_qty}주")
            print(f"예상 매도금액: ${expected_amount:,.2f}")
        else:
            print("TQQQ 보유 없음")

def run_tests():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()