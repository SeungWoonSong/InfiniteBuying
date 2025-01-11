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
    stock_code: str  # 종목 코드
    target_price: float  # 목표 매수가
    quantity: int  # 매수 수량
    first_buy_amount: float  # 첫 매수금액
    pre_turn_threshold: float  # 추가 매수 시작 기준 하락률 (%)
    quarter_loss_start: float  # 1/4 손절 시작 기준 하락률 (%)
    trading_interval: float  # 매매 주기 (초)
    max_trades_per_day: int  # 일일 최대 매매 횟수
    use_real_trading: bool  # 실제 매매 여부

class ConfigUpdate(BaseModel):
    """설정 업데이트"""
    bot_config: BotConfig
    trading_config: TradingConfig
