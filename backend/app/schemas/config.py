from pydantic import BaseModel

class TradingConfigUpdate(BaseModel):
    symbol: str
    total_divisions: int
    first_buy_amount: float
    pre_turn_threshold: int
    quarter_loss_start: float

class TradingConfigResponse(BaseModel):
    symbol: str
    total_divisions: int
    first_buy_amount: float
    pre_turn_threshold: int
    quarter_loss_start: float
    is_running: bool
