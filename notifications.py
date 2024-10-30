# notifications.py
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from typing import Optional
from decimal import Decimal

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_MY_ID')
        self.application = None

    async def initialize(self):
        """비동기 초기화"""
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("status", self.status_command))
        await self.application.initialize()
        await self.application.start()

    async def shutdown(self):
        """비동기 종료"""
        if self.application:
            await self.application.stop()
            
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """상태 확인 명령어"""
        await update.message.reply_text("봇이 정상 작동중입니다.")

    async def send_notification(self, message: str):
        if not self.application:
            await self.initialize()
            
        if not self.chat_id:
            raise ValueError("chat_id is not set")
            
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            raise  # 예외를 상위로 전파

    async def notify_order(self, order_type: str, symbol: str, qty: Optional[Decimal] = None, 
                         price: Optional[float] = None, amount: Optional[float] = None):
        """주문 관련 알림"""
        message = f"🔔 <b>{order_type}</b>\n"
        message += f"종목: {symbol}\n"
        
        if qty is not None:
            message += f"수량: {qty}주\n"
        if price is not None:
            message += f"가격: ${price:,.2f}\n"
        if amount is not None:
            message += f"금액: ${amount:,.2f}\n"
            
        message += f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await self.send_notification(message)

    async def notify_balance(self, account_balance: float, stocks: list):
        """계좌 잔고 알림"""
        message = "📊 <b>일일 계좌 현황</b>\n\n"
        message += f"💵 예수금: ${account_balance:,.2f}\n\n"
        
        if stocks:
            message += "📈 보유 주식:\n"
            for stock in stocks:
                message += (
                    f"- {stock['symbol']}: {stock['quantity']}주\n"
                    f"  평균단가: ${stock['average_price']:,.2f}\n"
                    f"  현재가: ${stock['current_price']:,.2f}\n"
                    f"  평가금액: ${stock['total_value']:,.2f}\n"
                    f"  수익률: {stock['profit_rate']:.2f}%\n\n"
                )
        else:
            message += "보유 주식 없음"
            
        await self.send_notification(message)

    async def notify_error(self, error: Exception):
        """에러 알림"""
        message = (
            f"⚠️ <b>에러 발생</b>\n"
            f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"에러: {str(error)}"
        )
        await self.send_notification(message)