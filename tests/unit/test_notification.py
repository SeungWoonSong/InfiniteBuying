import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from notifications import TelegramNotifier
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

class TestTelegramNotifier(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """비동기 설정"""
        # 실제 환경 변수 로드
        load_dotenv()
        
        # 실제 TelegramNotifier 초기화
        self.notifier = TelegramNotifier()
        await self.notifier.initialize()
        print("텔레그램 봇 초기화 완료")

    async def asyncTearDown(self):
        """비동기 정리"""
        await self.notifier.shutdown()
        print("텔레그램 봇 종료")

    async def test_notify_order(self):
        """주문 알림 테스트"""
        print("\n주문 알림 테스트 시작...")
        await self.notifier.notify_order(
            order_type="매수 주문",
            symbol="AAPL",
            qty=Decimal('10'),
            price=150.50,
            amount=1505.00
        )
        print("주문 알림 전송 완료")

    async def test_notify_balance(self):
        """잔고 알림 테스트"""
        print("\n잔고 알림 테스트 시작...")
        stocks = [{
            'symbol': 'AAPL',
            'quantity': 10,
            'average_price': 150.50,
            'current_price': 160.00,
            'total_value': 1600.00,
            'profit_rate': 6.31
        }]
        
        await self.notifier.notify_balance(10000.00, stocks)
        print("잔고 알림 전송 완료")

    async def test_notify_error(self):
        """에러 알림 테스트"""
        print("\n에러 알림 테스트 시작...")
        test_error = Exception("테스트 에러")
        await self.notifier.notify_error(test_error)
        print("에러 알림 전송 완료")

    async def test_empty_balance(self):
        """빈 잔고 알림 테스트"""
        print("\n빈 잔고 알림 테스트 시작...")
        await self.notifier.notify_balance(10000.00, [])
        print("빈 잔고 알림 전송 완료")

def run_tests():
    print("=== 텔레그램 알림 테스트 시작 ===")
    print("환경 변수 확인:")
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_MY_ID')
    print(f"Bot Token: {'설정됨' if token else '없음'}")
    print(f"Chat ID: {'설정됨' if chat_id else '없음'}")
    print("================================")
    
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()