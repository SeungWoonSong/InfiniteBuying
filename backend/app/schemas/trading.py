from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TradingStatus(BaseModel):
    current_price: float
    position_count: int
    average_price: float
    total_investment: float
    unrealized_pnl: float
    current_division: int
    last_updated: datetime

class TradeHistory(BaseModel):
    timestamp: datetime
    symbol: str
    action: str  # "BUY" or "SELL"
    price: float
    quantity: float
    division: int
    total_amount: float

class TradingStatusResponse(BaseModel):
    status: TradingStatus
    recent_trades: List[TradeHistory]
