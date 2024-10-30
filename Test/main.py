import os
from pathlib import Path
from pykis import PyKis
from dotenv import load_dotenv
from config import BotConfig, TradingConfig  # 이 부분이 누락되었습니다
from trading_bot import InfiniteBuyingBot

# 현재 디렉토리에서 .env 파일 로드
load_dotenv()

def main():
    try:
        # PyKis 인스턴스 생성
        kis = PyKis(
            id=os.getenv("ID"),
            account=os.getenv("ACCOUNT"),
            appkey=os.getenv("KIS_APPKEY"),
            secretkey=os.getenv("KIS_SECRETKEY"),
            virtual_id=os.getenv("ID"),
            virtual_appkey=os.getenv("VIRTUAL_KIS_APPKEY"),
            virtual_secretkey=os.getenv("VIRTUAL_KIS_SECRETKEY"),
            keep_token=True,
        )

        # 봇 설정
        bot_config = BotConfig(
            symbol="TQQQ",              # 매매할 종목
            total_divisions=40,         # 분할 횟수
            log_dir=Path("logs")        # 로그 저장 경로
        )
    
        # 매매 설정
        trading_config = TradingConfig(
            first_buy_amount=1,         # 첫 매수 수량
            pre_turn_threshold=20,      # 전반전/후반전 기준
            quarter_loss_start=39       # 쿼터손절 시작 회차
        )
    
        # 봇 생성 및 실행
        bot = InfiniteBuyingBot(kis, bot_config, trading_config)
        bot.run()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()