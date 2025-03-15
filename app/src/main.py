from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.db import init_db
from src.endpoints import agents, api

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

# CORS 설정: 모든 Origin 허용 (필요에 따라 조정 가능)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# API 라우터 등록
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(api.router, prefix="/api", tags=["API"])

app.mount("/", StaticFiles(directory="static", html=True), name="static")
