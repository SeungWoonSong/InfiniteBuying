FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt만 먼저 복사
COPY requirements.txt .

# 패키지 설치
RUN pip install --upgrade pip && \
    pip install aiohttp==3.9.1 && \
    pip install -r requirements.txt

# 앱 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
