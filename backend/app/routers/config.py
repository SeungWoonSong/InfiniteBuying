"""설정 관련 라우터"""
from fastapi import APIRouter, HTTPException
from ..schemas.config import ConfigUpdate as SchemaConfigUpdate
from ..schemas.config import BotConfig as SchemaBotConfig
from ..schemas.config import TradingConfig as SchemaTradingConfig
from ..trading.config import BotConfig, TradingConfig
from ..trading.bot_manager import bot_manager
import os
import json
from pathlib import Path

router = APIRouter(prefix="/config")

CONFIG_FILE = Path("data/config.json")
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

# 전역 설정 변수
_bot_config: BotConfig = None
_trading_config: TradingConfig = None

def create_default_config():
    """기본 설정 생성"""
    global _bot_config, _trading_config
    
    _bot_config = BotConfig(
        is_running=False,
        log_dir="logs",
        app_key=os.getenv("KIS_APPKEY"),
        app_secret=os.getenv("KIS_SECRETKEY"),
        account_number=os.getenv("ACCOUNT"),
        account_code="01"
    )
    
    _trading_config = TradingConfig(
        symbol="",
        total_divisions=40,
        first_buy_amount=1,
        pre_turn_threshold=20,
        quarter_loss_start=39,
        trading_interval=1.0
    )
    
    # 기본 설정을 파일에 저장
    save_config()

def load_config():
    """설정 파일 로드"""
    global _bot_config, _trading_config
    
    if not CONFIG_FILE.exists():
        create_default_config()
        return
    
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            if data:
                bot_data = data.get("bot_config", {})
                trading_data = data.get("trading_config", {})
                
                _bot_config = BotConfig(
                    is_running=bot_data.get("is_running", False),
                    log_dir="logs",  # 기본값 사용
                    app_key=os.getenv("KIS_APPKEY"),
                    app_secret=os.getenv("KIS_SECRETKEY"),
                    account_number=os.getenv("ACCOUNT"),
                    account_code="01"  # 기본값 사용
                )
                
                _trading_config = TradingConfig(
                    symbol=trading_data.get("symbol", ""),
                    total_divisions=trading_data.get("total_divisions", 40),
                    first_buy_amount=trading_data.get("first_buy_amount", 1),
                    pre_turn_threshold=trading_data.get("pre_turn_threshold", 20),
                    quarter_loss_start=trading_data.get("quarter_loss_start", 39),
                    trading_interval=1.0  # 기본값 사용
                )
            else:
                create_default_config()
    except Exception as e:
        print(f"Failed to load config: {e}")
        create_default_config()

def save_config():
    """설정 파일 저장"""
    if _bot_config is None or _trading_config is None:
        return
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "bot_config": {
                    "is_running": _bot_config.is_running,
                },
                "trading_config": {
                    "symbol": _trading_config.symbol,
                    "total_divisions": _trading_config.total_divisions,
                    "first_buy_amount": _trading_config.first_buy_amount,
                    "pre_turn_threshold": _trading_config.pre_turn_threshold,
                    "quarter_loss_start": _trading_config.quarter_loss_start,
                }
            }, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

# 시작할 때 설정 로드
load_config()

def convert_schema_to_bot_config(schema_config: SchemaBotConfig) -> BotConfig:
    """스키마 설정을 봇 설정으로 변환"""
    return BotConfig(
        is_running=schema_config.is_running,
        log_dir="logs",  # 기본값 사용
        app_key=os.getenv("KIS_APPKEY"),  # 환경 변수에서 가져옴
        app_secret=os.getenv("KIS_SECRETKEY"),
        account_number=os.getenv("ACCOUNT"),
        account_code="01"  # 기본값 사용
    )

def convert_schema_to_trading_config(schema_config: SchemaTradingConfig) -> TradingConfig:
    """스키마 설정을 거래 설정으로 변환"""
    return TradingConfig(
        symbol=schema_config.symbol,
        total_divisions=schema_config.total_divisions,
        first_buy_amount=schema_config.first_buy_amount,
        pre_turn_threshold=schema_config.pre_turn_threshold,
        quarter_loss_start=schema_config.quarter_loss_start,
        trading_interval=1.0  # 기본값 사용
    )

@router.get("")
async def get_config():
    """현재 설정 조회"""
    global _bot_config, _trading_config
    
    # 설정이 없으면 기본값 생성
    if _bot_config is None or _trading_config is None:
        create_default_config()
    
    return {
        "bot_config": {
            "is_running": _bot_config.is_running,
        },
        "trading_config": {
            "symbol": _trading_config.symbol,
            "total_divisions": _trading_config.total_divisions,
            "first_buy_amount": _trading_config.first_buy_amount,
            "pre_turn_threshold": _trading_config.pre_turn_threshold,
            "quarter_loss_start": _trading_config.quarter_loss_start,
        }
    }

@router.post("")
async def update_config(config: SchemaConfigUpdate):
    """설정 업데이트"""
    global _bot_config, _trading_config
    
    _bot_config = convert_schema_to_bot_config(config.bot_config)
    _trading_config = convert_schema_to_trading_config(config.trading_config)
    
    # 설정 파일에 저장
    save_config()
    
    # 봇 매니저에 설정 전달
    bot_manager.update_config(_bot_config, _trading_config)
    return {"status": "success"}

@router.post("/start")
async def start_bot():
    """봇 시작"""
    global _bot_config, _trading_config
    
    # 설정이 없으면 기본값 생성
    if _bot_config is None or _trading_config is None:
        create_default_config()
    
    try:
        bot_manager.start()
        
        # 봇 상태 업데이트 및 저장
        _bot_config.is_running = True
        save_config()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_bot():
    """봇 중지"""
    try:
        bot_manager.stop()
        
        # 봇 상태 업데이트 및 저장
        if _bot_config:
            _bot_config.is_running = False
            save_config()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_bot():
    """봇 초기화"""
    try:
        bot_manager.reset()
        
        # 설정 초기화
        global _bot_config, _trading_config
        _bot_config = None
        _trading_config = None
        
        # 설정 파일 삭제
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        
        # 기본 설정 생성
        create_default_config()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
