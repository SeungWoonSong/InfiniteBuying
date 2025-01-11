from pykis import PyKis
import json
from datetime import datetime, time, timedelta
import time as time_module
import logging
from typing import Optional
from decimal import Decimal
import math
from apscheduler.schedulers.background import BackgroundScheduler

from config import BotConfig, TradingConfig
from models import TradingState, StockBalance, OrderTracking  
from utils import setup_logging, get_current_time_kst, calculate_single_amount, calculate_loc_price
from notifications import TelegramNotifier
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler 

class InfiniteBuyingBot:
    def __init__(self, kis: PyKis, config: BotConfig, trading_config: TradingConfig):
        """
        무한매수법 봇 초기화
        """
        self.pending_orders = {}  # 미체결 주문 저장
        self.kis = kis
        self.config = config
        self.trading_config = trading_config
        self.stock = kis.stock(config.symbol)

        # 상태 파일 경로
        self.state_file = config.log_dir / "trading_state.json"

        # 상태 초기화 또는 로드
        self.state = self._load_state()

        # 로거 설정
        self.logger = setup_logging(config.log_dir, "InfiniteBuyingBot")

        # 텔레그램 알림 설정
        self.notifier = TelegramNotifier()

        # 일일 리포트 스케줄러 설정
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.send_daily_report,
            trigger='cron',
            hour=22,
            minute=30
        )
        self.scheduler.start()
        self.logger.info("Daily report scheduler started.")
    
    async def async_initialize(self):
        """비동기 봇 초기화"""
        try:
            # 텔레그램 봇 초기화
            self.logger.info("Initializing Telegram bot...")
            await self.notifier.initialize()
            self.logger.info("Telegram bot initialized successfully")

            # 스케줄러는 이미 __init__에서 시작됨
            
            # 시작 알림 전송
            self.logger.info("Sending start notification...")
            await self.notifier.notify_order(
                "봇 시작",
                self.stock.symbol,
                None,
                None,
                None
            )
            self.logger.info("Start notification sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {str(e)}", exc_info=True)
            raise
    
    def _load_state(self) -> TradingState:
        """저장된 상태 로드 또는 새로운 상태 생성"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return TradingState.from_dict(data)
        except Exception as e:
            print(f"Failed to load state: {e}")
        return TradingState()
    
    def _save_state(self):
        """현재 상태 저장"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def get_balance(self) -> Optional[StockBalance]:
        try:
            balance = self.kis.account().balance()
            stock = balance.stock(self.stock.symbol)
            self.usd_deposit = balance.deposits['USD'].amount  # USD 예수금 저장
            if stock:
                return StockBalance(
                    quantity=stock.qty,
                    average_price=stock.price,
                    current_price=self.stock.quote().price
                )
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            self.notifier.notify_error(e)
        return None

    async def send_daily_report(self):
        """일일 계좌 현황 리포트 전송"""
        try:
            balance = self.kis.account().balance()
            deposits = balance.deposits['USD'].amount  
            
            self.logger.info("Daily report job triggered.")

            stocks = []
            for stock in balance.stocks:
                quote = self.kis.stock(stock.symbol).quote()
                stocks.append({
                    'symbol': stock.symbol,
                    'quantity': stock.qty,
                    'average_price': stock.price,
                    'current_price': quote.price,
                    'total_value': float(stock.qty) * quote.price,
                    'profit_rate': ((quote.price - stock.price) / stock.price * 100)
                })
            
            await self.notifier.notify_balance(deposits, stocks)
            
        except Exception as e:
            self.logger.error(f"Failed to send daily report: {e}")
            await self.notifier.notify_error(e)

    def calculate_buy_quantity(self, amount: float, price: float) -> int:
        """매수 수량 계산 (정수로 반환)"""
        quantity = amount / price
        return math.floor(quantity)  # 소수점 이하 버림

    async def execute_first_buy(self):
        """첫 매수 실행"""
        try:
            quote = self.stock.quote()
            current_price = quote.price
            
            # 시장가 주문으로 1주 매수
            order = self.stock.buy(
                qty=self.trading_config.first_buy_amount,
                condition="MOC"
            )

            # 주문 추적 성공 시에만 상태 업데이트
            if await self.track_order(order):
                await self.notifier.notify_order(
                    "첫 매수 완료",
                    self.stock.symbol,
                    self.trading_config.first_buy_amount,
                    current_price,
                    current_price * self.trading_config.first_buy_amount
                )
                
                self.state.is_first_buy = False
                self.state.initial_price = current_price
                self._save_state()
                
        except Exception as e:
            self.logger.error(f"Error in first buy: {e}")
            await self.notifier.notify_error(e)

    async def _execute_pre_turn_trading(self, single_amount: float):
        """전반전 매매"""
        try:
            quote = self.stock.quote()
            current_price = quote.price
            half_amount = single_amount / 2
            
            # 0% LOC 매수
            qty = self.calculate_buy_quantity(half_amount, current_price)
            if qty > 0:
                order1 = self.stock.buy(
                    price=current_price,
                    qty=qty,
                    condition="LOC"
                )
                
                # 첫 번째 주문 추적 성공 시에만 두 번째 주문 실행
                if await self.track_order(order1):
                    await self.notifier.notify_order(
                        "전반전 0% LOC 매수 완료",
                        self.stock.symbol,
                        qty=qty,
                        price=current_price,
                        amount=current_price * qty
                    )
                    
                    # (10-T/2)% LOC 매수
                    percent = 10 - (self.state.turn/2)
                    price = calculate_loc_price(current_price, percent)
                    qty = self.calculate_buy_quantity(half_amount, price)
                    
                    if qty > 0:
                        order2 = self.stock.buy(
                            price=price - 0.01,
                            qty=qty,
                            condition="LOC"
                        )
                        
                        if await self.track_order(order2):
                            await self.notifier.notify_order(
                                f"전반전 {percent:.1f}% LOC 매수 완료",
                                self.stock.symbol,
                                qty=qty,
                                price=price - 0.01,
                                amount=price * qty
                            )
                    
            self.state.turn += 1
            self._save_state()
                    
        except Exception as e:
            self.logger.error(f"Error in pre turn trading: {e}")
            await self.notifier.notify_error(e)

    async def _execute_post_turn_trading(self, single_amount: float):
        """후반전 매매"""
        try:
            quote = self.stock.quote()
            current_price = quote.price
                
            percent = 10 - (self.state.turn/2)
            price = calculate_loc_price(current_price, percent)
            qty = self.calculate_buy_quantity(single_amount, price)
                
            if qty > 0:
                order = self.stock.buy(
                    price=price - 0.01,
                    qty=qty,
                    condition="LOC"
                )
                
                if await self.track_order(order):
                    await self.notifier.notify_order(
                        f"후반전 {percent:.1f}% LOC 매수 완료",
                        self.stock.symbol,
                        qty=qty,
                        price=price - 0.01,
                        amount=price * qty
                    )
                    
                    self.state.turn += 1
                    self._save_state()
                    
        except Exception as e:
            self.logger.error(f"Error in post turn trading: {e}")
            await self.notifier.notify_error(e)
                
    async def execute_normal_trading(self):
        """일반 매매 실행"""
        try:
            balance = self.get_balance()
            if not balance:
                return
                    
            # 현재 회차에서 사용할 1회 매수금액 계산
            remaining_capital = float(self.usd_deposit)
            remaining_turns = self.config.total_divisions - self.state.turn
                
            if remaining_turns <= 0:
                self.logger.info("All turns completed")
                return
                    
            single_amount = remaining_capital / remaining_turns
                
            # 전반전/후반전 매매 실행 
            if self.state.turn < self.trading_config.pre_turn_threshold:
                await self._execute_pre_turn_trading(single_amount)
            else:
                await self._execute_post_turn_trading(single_amount)
                    
            # 매도 주문 실행
            await self._execute_sell_orders(balance)
                
        except Exception as e:
            self.logger.error(f"Error in normal trading: {e}")
            await self.notifier.notify_error(e)

    async def _execute_sell_orders(self, balance: StockBalance):
        """매도 주문 실행"""
        try:
            if self.state.turn >= self.trading_config.quarter_loss_start:
                await self._execute_quarter_stop_loss(balance)
                return
                
            total_quantity = int(balance.quantity)
            quarter_quantity = total_quantity // 4
                
            if quarter_quantity == 0:
                return
                
            # (10-T/2)% LOC 매도
            percent = 10 - (self.state.turn/2)
            price = calculate_loc_price(balance.average_price, percent)
            order1 = self.stock.sell(
                price=price,
                qty=quarter_quantity,
                condition="LOC"
            )
        
            if await self.track_order(order1):
                await self.notifier.notify_order(
                    f"{percent:.1f}% LOC 매도 완료",
                    self.stock.symbol,
                    qty=quarter_quantity,
                    price=price,
                    amount=price * quarter_quantity
                )
                
                # 10% 지정가 매도
                remaining_qty = total_quantity - quarter_quantity
                if remaining_qty > 0:
                    price = calculate_loc_price(balance.average_price, 10)
                    order2 = self.stock.sell(
                        price=price,
                        qty=remaining_qty
                    )
                    
                    if await self.track_order(order2):
                        await self.notifier.notify_order(
                            "10% 지정가 매도 완료",
                            self.stock.symbol,
                            qty=remaining_qty,
                            price=price,
                            amount=price * remaining_qty
                        )
                    
        except Exception as e:
            self.logger.error(f"Error in sell orders: {e}")
            await self.notifier.notify_error(e)

    async def _execute_quarter_stop_loss(self, balance: StockBalance):
        """쿼터손절 실행"""
        try:
            total_quantity = int(balance.quantity)
            quarter_quantity = total_quantity // 4
                
            if quarter_quantity > 0:
                order = self.stock.sell(
                    qty=quarter_quantity,
                    condition="MOC"
                )
                
                if await self.track_order(order):
                    await self.notifier.notify_order(
                        "쿼터손절 MOC 매도 완료",
                        self.stock.symbol,
                        qty=quarter_quantity,
                        price=None,
                        amount=None
                    )
                    
        except Exception as e:
            self.logger.error(f"Error in quarter stop loss: {e}")
            await self.notifier.notify_error(e)

    async def check_cycle_completion(self) -> bool:
        try:
            balance = self.get_balance()
            
            # 이전 사이클이 완료되고 새 사이클을 시작하려는 경우
            if self.state.is_first_buy:
                return False  # 첫 매수를 기다리기 위해 false 반환
                
            # 보유 수량이 0이고 첫 매수가 아닌 경우 사이클 완료
            if balance is None or balance.quantity == 0:
                self.logger.info("Cycle completed. Starting new cycle...")
                await self.notifier.notify_order(
                    "🎉 사이클 완료",
                    self.stock.symbol,
                    qty=None,
                    price=None,
                    amount=None
                )
                self.state.reset()
                self._save_state()
                await asyncio.sleep(60)  # 새 사이클 시작 전 1분 대기
                return True
            return False
                
        except Exception as e:
            self.logger.error(f"Error in cycle completion check: {e}")
            await self.notifier.notify_error(e)
            return False

    async def run(self):
        """봇 실행"""
        self.logger.info(f"Bot started - Cycle {self.state.cycle_number}")
        
        while True:
            try:
                now = get_current_time_kst()
                
                # 장 마감시간 조회
                market_hours = self.kis.trading_hours("US")
                if isinstance(market_hours.close_kst, str):
                    close_time = datetime.strptime(market_hours.close_kst, '%H:%M:%S').time()
                else:
                    close_time = market_hours.close_kst
                
                # 장 마감 10분 전
                minute = close_time.minute - 10
                if minute < 0:
                    hour = (close_time.hour - 1) % 24
                    minute += 60
                else:
                    hour = close_time.hour
                target_time = time(hour=hour, minute=minute, second=0)

                current_time = now.time()
                
                # 장 마감 10분 전부터 5분 동안
                if target_time <= current_time <= time(target_time.hour, target_time.minute + 5):
                    if await self.check_cycle_completion():
                        continue
                    
                    if self.state.is_first_buy:
                        await self.execute_first_buy()
                    else:
                        await self.execute_normal_trading()
                    
                    self.logger.info("Waiting for next trading day...")
                    await asyncio.sleep(60 * 60 * 23 + 60 * 55)  # 23시간 55분 대기
                
                await asyncio.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await self.notifier.notify_error(e)
                self.logger.info("Restarting loop in 60 seconds...")
                await asyncio.sleep(60)
                # 에러가 발생해도 계속 실행
                continue

    async def track_order(self, order):
        """주문 추적"""
        try:
            if not hasattr(order, 'number'):
                self.logger.error("Invalid order object")
                return False
                
            tracking = OrderTracking(
                order_number=order.number,
                symbol=order.symbol,
                type=order.type,
                price=order.price,
                qty=order.qty,
                executed_qty=0,
                condition=order.condition, 
                time=datetime.now()
            )
            
            # 테스트 환경에서는 바로 체결된 것으로 처리
            if asyncio.get_event_loop().get_debug():
                tracking.executed_qty = tracking.qty
                return True
                
            self.pending_orders[order.number] = tracking
            
            retry_count = 0
            max_retries = 10
            
            while not tracking.is_complete and retry_count < max_retries:
                try:
                    pending = await self.kis.account().pending_orders()
                    current_order = pending.get(order.number)
                    
                    if current_order:
                        tracking.executed_qty = current_order.executed_qty
                    else:
                        tracking.executed_qty = tracking.qty
                        
                    if tracking.is_complete:
                        await self.notifier.notify_order(
                            f"{tracking.type} 주문 체결 완료",
                            tracking.symbol,
                            tracking.qty,
                            tracking.price,
                            tracking.price * tracking.qty
                        )
                        del self.pending_orders[order.number]
                        return True
                        
                    retry_count += 1
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error checking order status: {e}")
                    retry_count += 1
                    
            return tracking.is_complete
            
        except Exception as e:
            self.logger.error(f"Error tracking order: {e}")
            await self.notifier.notify_error(e)
            return False