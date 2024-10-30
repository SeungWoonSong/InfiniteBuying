# test_send.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from notifications import TelegramNotifier
from decimal import Decimal

async def test_send():
    notifier = TelegramNotifier()
    await notifier.initialize()
    
    try:
        # 테스트 메시지 전송
        print("주문 알림 테스트 전송 중...")
        await notifier.notify_order(
            order_type="테스트 주문",
            symbol="AAPL",
            qty=Decimal('10'),
            price=150.50,
            amount=1505.00
        )
        
        print("잔고 알림 테스트 전송 중...")
        await notifier.notify_balance(
            account_balance=10000.00,
            stocks=[{
                'symbol': 'AAPL',
                'quantity': 10,
                'average_price': 150.50,
                'current_price': 160.00,
                'total_value': 1600.00,
                'profit_rate': 6.31
            }]
        )
        
        print("에러 알림 테스트 전송 중...")
        await notifier.notify_error(Exception("테스트 에러 메시지"))
        
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        await notifier.shutdown()

if __name__ == "__main__":
    asyncio.run(test_send())