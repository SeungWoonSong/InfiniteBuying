from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import config, trading

app = FastAPI(title="Infinite Buying Bot")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
