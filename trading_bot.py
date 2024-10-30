from pykis import PyKis, KisStock
import json
from datetime import datetime, time, timedelta
import time as time_module
import logging
from typing import Optional
from decimal import Decimal
import math
from apscheduler.schedulers.background import BackgroundScheduler

from config import BotConfig, TradingConfig
from models import TradingState, StockBalance
from utils import setup_logging, get_current_time_kst, calculate_single_amount, calculate_loc_price
from notifications import TelegramNotifier

class InfiniteBuyingBot:
    def __init__(self, 
                 kis: PyKis, 
                 config: BotConfig,
                 trading_config: TradingConfig):
        """
        무한매수법 봇 초기화
        
        Args:
            kis: PyKis 인스턴스
            config: 봇 설정
            trading_config: 매매 설정
        """
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
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.send_daily_report,
            trigger='cron',
            hour=24,  # 저녁 12시
            minute=0
        )
        self.scheduler.start()
        
        self.logger.info(f"Bot initialized - Cycle {self.state.cycle_number}")
        self.notifier.notify_order(
            "봇 시작",
            self.stock.symbol,
            None,
            None,
            None
        )
    
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
        """현재 잔고 조회"""
        try:
            balance = self.kis.account().balance()
            stock = balance.stock(self.stock.symbol)
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

    def send_daily_report(self):
        """일일 계좌 현황 리포트 전송"""
        try:
            balance = self.kis.account().balance()
            deposits = sum(deposit.amount for deposit in balance.deposits.values())
            
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
            
            self.notifier.notify_balance(deposits, stocks)
            
        except Exception as e:
            self.logger.error(f"Failed to send daily report: {e}")
            self.notifier.notify_error(e)

    def calculate_buy_quantity(self, amount: float, price: float) -> int:
        """매수 수량 계산 (정수로 반환)"""
        quantity = amount / price
        return math.floor(quantity)  # 소수점 이하 버림

    def execute_first_buy(self):
        """첫 매수 실행"""
        try:
            quote = self.stock.quote()
            current_price = quote.price
            
            # 시장가 주문으로 1주 매수
            order = self.stock.buy(
                qty=self.trading_config.first_buy_amount,
                condition="MOC"
            )
            
            self.notifier.notify_order(
                "첫 매수 주문",
                self.stock.symbol,
                qty=self.trading_config.first_buy_amount,
                price=current_price,
                amount=current_price * self.trading_config.first_buy_amount
            )
            
            self.state.is_first_buy = False
            self.state.initial_price = current_price
            self._save_state()
            
        except Exception as e:
            self.logger.error(f"Error in first buy: {e}")
            self.notifier.notify_error(e)

    def _execute_pre_turn_trading(self, single_amount: float):
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
                
                self.notifier.notify_order(
                    "전반전 0% LOC 매수 주문",
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
                
                self.notifier.notify_order(
                    f"전반전 {percent:.1f}% LOC 매수 주문",
                    self.stock.symbol,
                    qty=qty,
                    price=price - 0.01,
                    amount=price * qty
                )
                
        except Exception as e:
            self.logger.error(f"Error in pre turn trading: {e}")
            self.notifier.notify_error(e)

    def _execute_post_turn_trading(self, single_amount: float):
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
                
                self.notifier.notify_order(
                    f"후반전 {percent:.1f}% LOC 매수 주문",
                    self.stock.symbol,
                    qty=qty,
                    price=price - 0.01,
                    amount=price * qty
                )
                
        except Exception as e:
            self.logger.error(f"Error in post turn trading: {e}")
            self.notifier.notify_error(e)

    def execute_normal_trading(self):
        """일반 매매 실행"""
        try:
            balance = self.get_balance()
            if not balance:
                return
                
            # 현재 회차에서 사용할 1회 매수금액 계산
            remaining_capital = self.state.total_investment - balance.total_value
            remaining_turns = self.config.total_divisions - self.state.turn
            
            if remaining_turns <= 0:
                self.logger.info("All turns completed")
                return
                
            single_amount = remaining_capital / remaining_turns
            
            if self.state.turn < self.trading_config.pre_turn_threshold:
                self._execute_pre_turn_trading(single_amount)
            else:
                self._execute_post_turn_trading(single_amount)
                
            self._execute_sell_orders(balance)
            
        except Exception as e:
            self.logger.error(f"Error in normal trading: {e}")
            self.notifier.notify_error(e)

    def _execute_sell_orders(self, balance: StockBalance):
        """매도 주문 실행"""
        try:
            if self.state.turn >= self.trading_config.quarter_loss_start:
                self._execute_quarter_stop_loss(balance)
                return
            
            total_quantity = int(balance.quantity)  # Decimal을 int로 변환
            quarter_quantity = total_quantity // 4  # 정수 나눗셈
            
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
            
            self.notifier.notify_order(
                f"{percent:.1f}% LOC 매도 주문",
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
                
                self.notifier.notify_order(
                    "10% 지정가 매도 주문",
                    self.stock.symbol,
                    qty=remaining_qty,
                    price=price,
                    amount=price * remaining_qty
                )
                
        except Exception as e:
            self.logger.error(f"Error in sell orders: {e}")
            self.notifier.notify_error(e)

    def _execute_quarter_stop_loss(self, balance: StockBalance):
        """쿼터손절 실행"""
        try:
            total_quantity = int(balance.quantity)
            quarter_quantity = total_quantity // 4
            
            if quarter_quantity > 0:
                order = self.stock.sell(
                    qty=quarter_quantity,
                    condition="MOC"
                )
                
                self.notifier.notify_order(
                    "쿼터손절 MOC 매도 주문",
                    self.stock.symbol,
                    qty=quarter_quantity,
                    price=None,    # 키워드 인자로 변경
                    amount=None    # 키워드 인자로 변경
                )
                
        except Exception as e:
            self.logger.error(f"Error in quarter stop loss: {e}")
            self.notifier.notify_error(e)

    def check_cycle_completion(self) -> bool:
        """사이클 완료 여부 확인"""
        try:
            balance = self.get_balance()
            # balance가 None이거나 수량이 0인 경우를 체크
            if balance is None or balance.quantity == 0:
                self.logger.info("Cycle completed. Starting new cycle...")
                self.notifier.notify_order(
                    "🎉 사이클 완료",
                    self.stock.symbol,
                    qty=None,
                    price=None,
                    amount=None
                )
                self.state.reset()
                self._save_state()
                return True
            return False
                
        except Exception as e:
            self.logger.error(f"Error in cycle completion check: {e}")
            self.notifier.notify_error(e)
            return False

    def run(self):
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
                    close_time = market_hours.close_kst  # 이미 time 객체인 경우
                
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
                if (target_time <= current_time <= 
                    time(target_time.hour, target_time.minute + 5)):
                    
                    # 사이클 완료 체크
                    if self.check_cycle_completion():
                        continue
                    
                    # 첫 매수 또는 일반 매매
                    if self.state.is_first_buy:
                        self.execute_first_buy()
                    else:
                        self.execute_normal_trading()
                    
                    # 다음날까지 대기
                    self.logger.info("Waiting for next trading day...")
                    time_module.sleep(60 * 60 * 23 + 60 * 55)
                
                time_module.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.notifier.notify_error(e)
                self.logger.info("Restarting bot in 60 seconds...")
                time_module.sleep(60)