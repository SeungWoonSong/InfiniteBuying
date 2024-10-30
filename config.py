# config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class BotConfig:
    """봇 설정"""
    symbol: str                     # 매매할 종목 심볼
    total_divisions: int = 40       # 분할 횟수
    log_dir: Path = Path("logs")    # 로그 디렉토리
    
    def __post_init__(self):
        self.log_dir.mkdir(exist_ok=True)
        
@dataclass
class TradingConfig:
    """매매 설정"""
    first_buy_amount: float = 1     # 첫 매수 수량 (주)
    pre_turn_threshold: int = 20    # 전반전/후반전 기준
    quarter_loss_start: float = 39  # 쿼터손절 시작 회차