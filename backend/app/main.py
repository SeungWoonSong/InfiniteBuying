from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import config, trading

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(config.router, prefix="")
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])