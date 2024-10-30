# utils.py
import logging
from datetime import datetime, time
import pytz
from pathlib import Path

def setup_logging(log_dir: Path, name: str) -> logging.Logger:
    """로깅 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 로그 파일명에 날짜 추가
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷터
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_current_time_kst() -> datetime:
    """현재 KST 시간 반환"""
    return datetime.now(pytz.timezone('Asia/Seoul'))

def calculate_single_amount(total_capital: float, total_divisions: int) -> float:
    """1회 매수금액 계산"""
    return total_capital / total_divisions

def calculate_loc_price(base_price: float, percent: float) -> float:
    """LOC 주문 가격 계산"""
    return base_price * (1 + percent/100)