"""설정 관련 라우터"""
from fastapi import APIRouter, HTTPException
from trading.config import ConfigUpdate, BotConfig, TradingConfig
from trading.bot_manager import bot_manager

router = APIRouter()

# 전역 설정 변수
_bot_config: BotConfig = None
_trading_config: TradingConfig = None

@router.get("/config")
async def get_config():
    """현재 설정 조회"""
    if _bot_config is None or _trading_config is None:
        return None
    return {
        "bot_config": _bot_config.model_dump(),
        "trading_config": _trading_config.model_dump()
    }

@router.post("/config")
async def update_config(config: ConfigUpdate):
    """설정 업데이트"""
    global _bot_config, _trading_config
    try:
        _bot_config = config.bot_config
        _trading_config = config.trading_config
        await bot_manager.initialize_bot(_bot_config, _trading_config)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

@router.post("/bot/start")
async def start_bot():
    """봇 시작 엔드포인트"""
    try:
        await bot_manager.start()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bot/stop")
async def stop_bot():
    """봇 중지 엔드포인트"""
    try:
        await bot_manager.stop()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bot/reset")
async def reset_bot():
    """봇 초기화 엔드포인트"""
    try:
        await bot_manager.reset()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/bot/status")
async def get_status():
    """봇 상태 조회 엔드포인트"""
    return {"is_running": bot_manager.is_running()}
