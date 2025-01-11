from fastapi import APIRouter, HTTPException
from trading.bot_manager import bot_manager
from trading.config import ConfigUpdate

router = APIRouter()

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}

@router.get("/config")
async def get_config():
    """설정 조회 엔드포인트"""
    return {
        "bot_config": bot_manager._bot.bot_config if bot_manager._bot else None,
        "trading_config": bot_manager._bot.trading_config if bot_manager._bot else None
    }

@router.post("/config")
async def update_config(config: ConfigUpdate):
    """설정 업데이트 엔드포인트"""
    if bot_manager.get_status():
        raise HTTPException(status_code=400, detail="Bot is running")
    await bot_manager.initialize_bot(config.bot_config, config.trading_config)
    return {"success": True}

@router.post("/config/start")
async def start_bot():
    """봇 시작 엔드포인트"""
    if bot_manager._bot is None:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    await bot_manager.start()
    return {"success": True}

@router.post("/config/stop")
async def stop_bot():
    """봇 중지 엔드포인트"""
    if bot_manager._bot is None:
        raise HTTPException(status_code=400, detail="Bot not initialized")
    await bot_manager.stop()
    return {"success": True}

@router.post("/config/reset")
async def reset_bot():
    """봇 초기화 엔드포인트"""
    if bot_manager._bot is not None:
        await bot_manager.stop()
    bot_manager.reset()
    return {"success": True}

@router.get("/config/status")
async def get_status():
    """봇 상태 조회 엔드포인트"""
    return {"is_running": bot_manager.get_status()}
