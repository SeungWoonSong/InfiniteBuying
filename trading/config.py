from pathlib import Path
from typing import Optional
from pydantic import BaseModel

class BotConfig(BaseModel):
    """봇 설정"""
    symbol: str  # 종목 코드 (예: "005930")
    total_divisions: int  # 총 분할 매수 횟수
    log_dir: str  # 로그 디렉토리
    app_key: str  # 한국투자증권 앱키
    app_secret: str  # 한국투자증권 시크릿
    account_number: str  # 계좌번호
    account_code: str  # 계좌코드 (01: 주식)

class TradingConfig(BaseModel):
    """거래 설정"""
    initial_amount: float  # 초기 투자금액
    single_amount: float  # 1회 매수금액
    min_order_amount: float  # 최소 주문금액
    loss_cut_rate: float  # 손절률
    profit_rate: float  # 익절률
    max_buy_times: int  # 최대 매수 횟수
    trading_interval: float = 1.0  # 매매 주기 (초)

class ConfigUpdate(BaseModel):
    """설정 업데이트"""
    bot_config: BotConfig
    trading_config: TradingConfig
