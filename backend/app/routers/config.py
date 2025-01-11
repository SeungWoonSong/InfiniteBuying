from fastapi import APIRouter, HTTPException
from ..schemas.config import TradingConfigUpdate, TradingConfigResponse
import json
from pathlib import Path
from trading.bot_manager import bot_manager
from trading.config import BotConfig, TradingConfig

router = APIRouter()

CONFIG_FILE = Path("trading/config.json")

def load_config():
    if not CONFIG_FILE.exists():
        return {
            "symbol": "TQQQ",
            "total_divisions": 40,
            "first_buy_amount": 1,
            "pre_turn_threshold": 20,
            "quarter_loss_start": 39,
            "is_running": False
        }
    return json.loads(CONFIG_FILE.read_text())

def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

@router.get("/config", response_model=TradingConfigResponse)
async def get_config():
    return load_config()

@router.post("/config", response_model=TradingConfigResponse)
async def update_config(config: TradingConfigUpdate):
    current_config = load_config()
    new_config = {**current_config, **config.dict()}
    save_config(new_config)
    
    # 봇 설정 업데이트
    bot_config = BotConfig(
        symbol=new_config["symbol"],
        total_divisions=new_config["total_divisions"],
        log_dir=Path("logs")
    )
    
    trading_config = TradingConfig(
        first_buy_amount=new_config["first_buy_amount"],
        pre_turn_threshold=new_config["pre_turn_threshold"],
        quarter_loss_start=new_config["quarter_loss_start"]
    )
    
    await bot_manager.initialize_bot(bot_config, trading_config)
    return new_config

@router.post("/start")
async def start_bot():
    config = load_config()
    if await bot_manager.start_bot():
        config["is_running"] = True
        save_config(config)
        return {"status": "Bot started"}
    raise HTTPException(status_code=400, detail="Failed to start bot")

@router.post("/stop")
async def stop_bot():
    config = load_config()
    if await bot_manager.stop_bot():
        config["is_running"] = False
        save_config(config)
        return {"status": "Bot stopped"}
    raise HTTPException(status_code=400, detail="Failed to stop bot")
