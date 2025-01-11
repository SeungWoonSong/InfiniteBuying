from fastapi import APIRouter, HTTPException
from ..schemas.trading import TradingStatus, TradeHistory, TradingStatusResponse
from datetime import datetime
from trading.bot_manager import bot_manager
from typing import List

router = APIRouter()

@router.get("/status", response_model=TradingStatusResponse)
async def get_trading_status():
    status = bot_manager.get_status()
    if not status:
        raise HTTPException(status_code=404, detail="Bot is not running")
    
    recent_trades = bot_manager.get_trade_history()[-10:]  # 최근 10개 거래내역
    return TradingStatusResponse(status=TradingStatus(**status), recent_trades=recent_trades)

@router.get("/history", response_model=List[TradeHistory])
async def get_trade_history(limit: int = 100, offset: int = 0):
    history = bot_manager.get_trade_history()
    return history[offset:offset + limit]
