from pathlib import Path
from typing import Optional
from pydantic import BaseModel

class BotConfig(BaseModel):
    """봇 설정"""
    is_running: bool = False
    log_dir: str = "logs"  # 로그 디렉토리
    app_key: Optional[str] = None  # 한국투자증권 앱키
    app_secret: Optional[str] = None  # 한국투자증권 시크릿
    account_number: Optional[str] = None  # 계좌번호
    account_code: str = "01"  # 계좌코드 (01: 주식)

class TradingConfig(BaseModel):
    """거래 설정"""
    symbol: str  # 종목 코드 (예: "005930")
    total_divisions: int  # 총 분할 매수 횟수
    first_buy_amount: float  # 첫 매수금액
    pre_turn_threshold: int  # 선행 턴 임계값
    quarter_loss_start: float  # 1/4 손실 시작점
    trading_interval: float = 1.0  # 매매 주기 (초)

class ConfigUpdate(BaseModel):
    """설정 업데이트"""
    bot_config: BotConfig
    trading_config: TradingConfig
