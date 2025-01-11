FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치 (캐시 레이어 최적화)
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt만 먼저 복사
COPY requirements.txt .

# 패키지 설치 (캐시 레이어 최적화)
RUN pip install --no-cache-dir fastapi uvicorn[standard] && \
    pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# FastAPI 서버 실행
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
