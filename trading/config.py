from pydantic import BaseModel
from typing import Optional

class BotConfig(BaseModel):
    """봇 기본 설정"""
    app_key: str
    app_secret: str
    account_number: str
    account_code: str = "01"  # 보통 01은 위탁계좌
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class TradingConfig(BaseModel):
    """트레이딩 설정"""
    stock_code: str
    target_price: float
    quantity: int
    trading_interval: int = 60  # 초 단위
    max_trades_per_day: int = 10
    use_real_trading: bool = False
