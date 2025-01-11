# 주식 매매 봇 프로젝트 - Infinite Buying Bot

본 프로젝트는 주식 자동 매매 봇으로, 무한 매수 전략을 기반으로 설계되었습니다. `Infinite Buying Bot`은 Python으로 구현되었으며, 매수 및 매도 로직을 포함하여 자동으로 거래를 수행합니다.

**현재는 한국투자증권에서만 사용가능합니다.**

## 파일 구조
```
.
├── README.md
├── Test
│   ├── __init__.py
│   ├── requirements-test.txt
│   ├── test_notification.py
│   ├── test_send.py
│   └── test_trading_bot.py
├── config.py
├── main.py
├── models.py
├── notifications.py
├── requirements.txt
├── trading_bot.py
├── utils.py
```

> 일부 파일 및 디렉토리는 `.gitignore`에 의해 Git에 포함되지 않습니다:
```
*.env
logs/
__pycache__
```

## 주요 파일 설명

### 1. `main.py`
- 봇 실행의 메인 진입점입니다. PyKis API를 통해 매매 봇을 초기화하고 실행하는 역할을 합니다. `.env` 파일에서 API 키 및 계정 정보를 로드합니다.
- `InfiniteBuyingBot`을 초기화하고 실행하기 위한 설정(`BotConfig`, `TradingConfig`)을 수행합니다.

### 2. `config.py`
- 봇의 설정을 담고 있는 파일로, `BotConfig`와 `TradingConfig` 클래스가 정의되어 있습니다.
  - `BotConfig`: 매매할 종목 심볼, 분할 횟수 및 로그 디렉토리를 설정합니다.
  - `TradingConfig`: 첫 매수 수량, 전반전/후반전 기준, 쿼터손절 시작 회차 등의 매매 설정을 포함합니다.

### 3. `models.py`
- 매매 상태와 주식 잔고 정보를 모델링한 파일입니다.
  - `TradingState`: 매매 상태를 저장하는 데이터 클래스입니다. 사이클 번호, 회차, 첫 매수 여부 등을 관리하며 새 사이클을 시작할 때 초기화할 수 있습니다.
  - `StockBalance`: 보유 주식 수량, 평균 단가, 현재가 등을 포함하는 주식 잔고 정보를 관리합니다.

### 4. `notifications.py`
- 텔레그램 알림 관련 기능을 담당하는 파일입니다.
  - `TelegramNotifier`: 텔레그램 봇을 통해 매수/매도 알림, 계좌 잔고 알림, 에러 알림을 전송합니다. 비동기 방식으로 구현되어 있으며, 봇 초기화 및 종료, 메시지 전송 기능이 포함되어 있습니다.

### 5. `trading_bot.py`
- 봇의 핵심 로직이 구현된 파일로, `InfiniteBuyingBot` 클래스가 정의되어 있습니다. PyKis API와 통신하여 매수 및 매도 로직을 수행하며, 매매 상태를 저장 및 로드합니다.
  - 첫 매수, 전반전/후반전 매매, 매도, 쿼터손절 등의 전략을 수행합니다.
  - 일일 계좌 현황 리포트를 전송하고 사이클 완료 여부를 체크하는 기능도 포함되어 있습니다.

### 6. `utils.py`
- 유틸리티 함수들을 모아놓은 파일로, 로깅 설정, 현재 KST 시간 반환, LOC 주문 가격 계산 등의 기능을 제공합니다.

### 7. `Test`
- 테스트 관련 파일들이 모여 있는 디렉토리입니다. 각 테스트는 `unittest`를 사용해 작성되었습니다.
  - `test_notification.py`: 텔레그램 알림 기능의 테스트입니다. 비동기 알림 전송, 잔고 알림, 에러 알림 등을 테스트합니다.
  - `test_send.py`: `TelegramNotifier`의 알림 기능을 직접 테스트하기 위한 파일입니다.
  - `test_trading_bot.py`: `InfiniteBuyingBot`의 매매 로직과 상태 관리 기능을 테스트합니다. 매수, 매도, 쿼터손절 등의 시나리오를 모킹(mocking)하여 검증합니다.

## 설치 및 실행 방법

### 요구 사항
- Python 3.10+
- `.env` 파일에 PyKis API와 텔레그램 봇의 설정 필요

### 설치
1. 리포지토리 클론
   ```sh
   git clone https://github.com/SeungWoonSong/InfiniteBuying.git
   cd InfiniteBuying
   ```

2. 패키지 설치
   ```sh
   pip install -r requirements.txt
   ```

3. `.env` 파일 설정
   - 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음과 같은 내용으로 API 및 계정 정보를 설정합니다.
   ```
   ID=사용자_ID
   ACCOUNT=계정_정보
   KIS_APPKEY=API_앱키
   KIS_SECRETKEY=API_시크릿키
   TELEGRAM_BOT_TOKEN=텔레그램_봇_토큰
   TELEGRAM_MY_ID=텔레그램_챗_ID
   ```

### 실행
```sh
python main.py
```

## Docker Compose로 실행하기

### 요구사항
- Docker
- Docker Compose
- 한국투자증권 계정 (실전 및 모의투자)
- 텔레그램 봇 토큰 및 채팅 ID

### 설치 및 실행 방법

1. 리포지토리 클론
   ```sh
   git clone https://github.com/SeungWoonSong/InfiniteBuying.git
   cd InfiniteBuying
   ```

2. 환경 변수 설정
   - `.env` 파일을 프로젝트 루트 디렉토리에 생성하고 다음 정보를 **모두** 입력해야 합니다:
   ```env
   # 한국투자증권 실전 API 설정
   ID=사용자_ID                    # 필수: 한국투자증권 ID
   ACCOUNT=계정_정보              # 필수: 계좌번호 앞 8자리
   KIS_APPKEY=실전_API_앱키       # 필수: 한국투자증권 실전 API 앱키
   KIS_SECRETKEY=실전_API_시크릿키 # 필수: 한국투자증권 실전 API 시크릿키
   
   # 한국투자증권 모의투자 API 설정
   VIRTUAL_KIS_APPKEY=모의투자_API_앱키       # 필수: 모의투자 API 앱키
   VIRTUAL_KIS_SECRETKEY=모의투자_API_시크릿키 # 필수: 모의투자 API 시크릿키
   
   # 텔레그램 봇 설정
   TELEGRAM_BOT_TOKEN=텔레그램_봇_토큰  # 필수: 텔레그램 봇 토큰
   TELEGRAM_MY_ID=텔레그램_챗_ID       # 필수: 텔레그램 채팅 ID
   ```

3. Docker Compose로 서비스 실행
   ```sh
   # 서비스 빌드 및 시작
   docker-compose up -d --build
   ```

4. 웹 인터페이스 사용하기
   - 브라우저에서 `http://localhost:5173` 접속
   
   a) 봇 설정하기
      - 매매할 종목 선택 (예: 005930 삼성전자)
      - 분할 매수 횟수 설정
      - 첫 매수 수량 입력
      - 전반전/후반전 기준 설정
      - 쿼터손절 시작 회차 설정
   
   b) 봇 제어하기
      - Start: 설정된 내용으로 봇 시작 (한 번에 하나의 봇만 실행 가능)
      - Stop: 현재 실행 중인 봇 중지
      - Reset: 봇 초기화 (거래 기록 초기화)
   
   c) 상태 확인
      - 현재 설정값 확인
      - 예상 매매 동작 확인
      - 실시간 거래 내역 확인
   
   d) 설정 변경
      - Stop 버튼으로 봇 중지
      - 새로운 설정 입력
      - Start 버튼으로 봇 재시작

5. 거래 내역 확인
   - 웹 인터페이스 하단에서 모든 거래 내역 확인 가능
   - 주문 시간, 종목, 매수/매도 여부, 수량, 가격 등 상세 정보 제공
   - 텔레그램으로도 실시간 알림 발송

6. 서비스 중지
   ```sh
   # 서비스 중지
   docker-compose down
   ```

## 테스트 실행
```sh
cd Test
python -m unittest discover
```

## 주의 사항
- 주식 거래와 관련된 API를 사용하기 때문에, 테스트나 실제 거래 시 실제 계좌에 영향을 미칠 수 있습니다. 테스트 환경과 실제 환경을 구분하여 진행하시기 바랍니다.

## 라이선스
- 본 프로젝트는 MIT 라이선스를 따릅니다.
