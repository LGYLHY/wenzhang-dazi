# 文案搭子 · AI 朋友圈文案生成器

> 输入心情/一张图，AI 现场创作 3 条不同风格的朋友圈文案；模板广场、AI 润色、收藏记忆，一条龙搞定朋友圈。

**技术栈**：Vue 3 + Vite · FastAPI + Uvicorn · SQLite · ChromaDB · 通义千问（qwen-vl-plus 看图 / qwen-turbo 润色）

---

## 功能一览（5 大页面）

| 页面 | 功能 |
|---|---|
| **生成** | 输入文字或上传图片 → AI 生成 3 条不同风格文案（逐字打字机效果）→ 复制 / 收藏 / 换一条；人设记忆自动参考你的历史偏好 |
| **收藏** | 本地收藏（localStorage），按情绪分组，复制 / 删除 / 一键清空 |
| **广场** | 5 类 40 个模板（旅行/美食/情感/节日/带货），每个模板 3 条示例可单独点选预载 |
| **润色** | 5 种风格 AI 改写：更文艺 / 更简短 / 加 emoji / 更幽默 / 更治愈 |
| **我的** | 使用说明 / 隐私说明 / 常见问题 |

## 快速开始

> **没有 API Key 也能运行！** 未配置 Key 时自动走 **mock 演示模式**（内置 62 条文案 + 关键词联想，功能完整）；配置 Key 后走真实 AI。

### 前置环境（先装这两个）

- **Python** 3.11+：https://www.python.org/downloads/ （✅ 必须勾选 "Add Python to PATH"）
- **Node.js 22 LTS 或更新**：https://nodejs.org/ （⚠️ **Node 20 在 Windows 上 npm install 有 race condition bug，必须 22+**）

### 方式一：一键启动（推荐）

```bash
# Windows：双击 start.bat
# macOS / Linux：
./start.sh
```

脚本会自动：首次安装依赖 → 启动前后端 → 打开浏览器（Windows 停止用 `stop.bat`）。

### 方式二：手动启动

**后端**

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --port 8000
```

**配置 API Key（可选）**：在 `backend/` 下创建 `.env`：

```
DASHSCOPE_API_KEY=sk-你的通义千问Key
```

**前端**

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

Vite 已把 `/api/*` 代理到 `http://127.0.0.1:8000`。

### 3. 测试

```bash
cd backend && pytest -q          # 后端契约测试
cd frontend && npx vitest run    # 前端单测
```

## 文档导航

| 文档 | 说明 |
|---|---|
| `docs/PRD.md` | 产品需求文档（目标、用户画像、功能需求 FR1~FR8、非功能需求） |
| `docs/设计文档.md` | 设计 Token、页面清单、交互流程、异常处理、响应式断点 |
| `docs/开发规划.md` | 里程碑 M0~M4、风险矩阵、质量门 |
| `docs/DEPLOYMENT.md` | 部署手册（CDN + 容器 + HTTPS + 隐私自检） |
| `docs/测试用例_M0_M1.md` ~ `M4` | 分阶段测试用例（契约/功能/异常/性能/隐私） |

## 目录结构

```
├── backend/
│   ├── app/
│   │   ├── data/          # SQLite + ChromaDB（初始化、人设记忆）
│   │   ├── routers/       # generate / polish / templates / persona / emotions
│   │   ├── services/      # 多模态调用（qwen-vl-plus + mock 兜底）、润色 LLM
│   │   ├── schemas.py     # Pydantic 模型
│   │   └── errors.py      # 统一错误信封（5 类业务异常）
│   ├── tests/             # pytest 契约测试
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # fetch 封装 + ApiError
│   │   ├── stores/        # toast / errorBar / deviceId / draft / history
│   │   ├── components/    # ResultCard / TonePills / ImageUploader / BottomTabBar...
│   │   ├── views/         # Generate / Collection / TemplateSquare / Polish / Help
│   │   └── assets/styles/ # design tokens / layout / components
│   ├── tests/             # vitest 单测 + e2e
│   └── package.json
└── docs/                  # 需求 / 设计 / 规划 / 测试用例 / 部署
```

## 隐私合规

- **服务端不落盘原图**：图片仅请求中转给模型，不留存。
- **不留存人脸**：ChromaDB 仅存文案文本向量。
- **本地优先**：收藏、草稿存浏览器 localStorage，可一键清空。
- **限流保护**：30 秒内 10 次生成，防止滥用。

## 后续可选迭代

真实 SSE 流式输出 · 跨设备同步 · 风格画像可视化 · B 端模板市场
