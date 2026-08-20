"""文案搭子后端入口 · FastAPI + Uvicorn"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import generate, templates, persona, polish
from app.data.db import init_db
from app.data.chroma_client import ensure_chroma
from app.services.llm_client import USE_MOCK


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化 SQLite + ChromaDB；关闭时不落盘原图，不留任务状态"""
    init_db()
    ensure_chroma()
    yield


app = FastAPI(
    title="文案搭子 API",
    version="0.1.0",
    description="AI 朋友圈文案生成器（MVP）",
    lifespan=lifespan,
)

# CORS：MVP 仅对前端开发服务器开放
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(persona.router, prefix="/api/persona")
app.include_router(polish.router, prefix="/api")


@app.get("/api/health")
def health():
    """健康检查；mock=true 表示当前为演示文案（未配置 LLM API Key）"""
    return {"status": "ok", "version": "0.1.0", "mock": USE_MOCK}
