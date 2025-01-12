from pydantic import BaseModel

class BotConfig(BaseModel):
    is_running: bool = False

class TradingConfig(BaseModel):
    symbol: str
    total_divisions: int
    first_buy_amount: float
    pre_turn_threshold: int
    quarter_loss_start: float

class ConfigUpdate(BaseModel):
    bot_config: BotConfig
    trading_config: TradingConfig
