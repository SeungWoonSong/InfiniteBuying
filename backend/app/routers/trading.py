"""거래 관련 라우터"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..schemas.trading import TradingStatus, TradeHistory, TradingStatusResponse
from ..trading.bot_manager import bot_manager
from datetime import datetime

router = APIRouter(prefix="/trading")

@router.get("/status", response_model=TradingStatusResponse)
async def get_trading_status():
    """거래 상태 조회"""
    if not bot_manager.is_running():
        trading_status = TradingStatus(
            current_price=0,
            position_count=0,
            average_price=0,
            total_investment=0,
            unrealized_pnl=0,
            current_division=0,
            last_updated=datetime.now()
        )
        return TradingStatusResponse(status=trading_status, recent_trades=[])
    
    # 기본 상태 정보 생성
    trading_status = TradingStatus(
        current_price=0,
        position_count=0,
        average_price=0,
        total_investment=0,
        unrealized_pnl=0,
        current_division=0,
        last_updated=datetime.now()
    )
    
    # 거래 내역을 TradeHistory 형식으로 변환
    recent_trades = []
    for trade in bot_manager.get_trade_history()[-10:]:
        recent_trades.append(TradeHistory(
            timestamp=trade.get("timestamp", datetime.now()),
            symbol=trade.get("symbol", ""),
            action=trade.get("action", ""),
            price=trade.get("price", 0),
            quantity=trade.get("quantity", 0),
            division=trade.get("division", 0),
            total_amount=trade.get("total_amount", 0)
        ))
    
    return TradingStatusResponse(status=trading_status, recent_trades=recent_trades)

@router.get("/history", response_model=List[TradeHistory])
async def get_trade_history(limit: int = 100, offset: int = 0):
    """거래 내역 조회"""
    history = []
    for trade in bot_manager.get_trade_history()[offset:offset + limit]:
        history.append(TradeHistory(
            timestamp=trade.get("timestamp", datetime.now()),
            symbol=trade.get("symbol", ""),
            action=trade.get("action", ""),
            price=trade.get("price", 0),
            quantity=trade.get("quantity", 0),
            division=trade.get("division", 0),
            total_amount=trade.get("total_amount", 0)
        ))
    return history
