"""文案搭子后端入口 · FastAPI + Uvicorn"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import generate, templates, persona, polish
from app.data.db import init_db
from app.data.chroma_client import ensure_chroma
from app.services.llm_client import USE_MOCK

# 前端构建产物目录：frontend/dist（由 `npm run build` 生成，已提交到仓库）。
# 存在时由后端直接托管，下载者无需 Node / npm 即可运行。
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"


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


# ---- 前端静态托管（生产构建产物 frontend/dist）----
# 若 dist 存在，则由后端直接托管前端；/api 仍由上面的路由处理，
# 其余路径回退到 index.html 以支持 SPA 前端路由（history 模式）。
if DIST_DIR.exists():
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        candidate = DIST_DIR / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(DIST_DIR / "index.html"))
