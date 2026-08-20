# 文案搭子 · 后端

> FastAPI + Uvicorn + SQLite + ChromaDB（M0 脚手架 + M1 识图生成核心链路）

## 目录

```
backend/
├── app/
│   ├── __init__.py            # FastAPI 入口 + lifespan 初始化 DB/Chroma
│   ├── schemas.py             # Pydantic 入参/出参
│   ├── errors.py              # 统一错误信封 {code, message}
│   ├── routers/
│   │   ├── generate.py        # POST /api/generate（M1 核心）
│   │   ├── templates.py       # GET  /api/templates（M3 占位）
│   │   └── persona.py         # POST /api/persona/upsert|recall（M2）
│   ├── services/
│   │   ├── llm_client.py      # Qwen-VL（主） / GLM-4V（备） / Mock 兜底
│   │   └── prompt_builder.py  # Prompt 拼装 + persona 注入
│   └── data/
│       ├── db.py              # SQLite + 种子模板
│       └── chroma_client.py   # 文案向量（不含图片/人脸）
└── tests/
    └── test_generate.py       # M0+M1 阶段用例（见 docs/测试用例_M0_M1.md）
```

## 运行

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

环境变量：
- `DASHSCOPE_API_KEY`：通义千问 VL（主）。**未设置时自动走 mock**，保证开发/演示闭环。
- `GLM_API_KEY`：智谱 GLM-4V（备）。
- `CHROMA_PERSIST_DIR`：可选，自定义 Chroma 持久化路径。

## 接口一览（M0 阶段）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET  | `/api/health` | 健康检查 |
| GET  | `/api/emotions` | 8 色情绪映射 |
| GET  | `/api/templates` | 模板列表（M3 用） |
| POST | `/api/generate` | **M1** 识图生成 |
| POST | `/api/persona/upsert` | 文案回流入向量（M2 用） |
| POST | `/api/persona/recall` | 风格召回（M2 用） |

## 隐私

- **服务端不落盘原图**：image_base64 仅在请求中暂存于内存，转给模型后丢弃。
- **不留存人脸**：ChromaDB 只存文案文本向量，不存图片/人脸。
- **数据最小化**：device_id 区分用户，避免收集 PII。
