# 文案搭子 · 部署手册（M4）

> 目标：前端静态托管（CDN）+ 后端容器，全链路 HTTPS。
> 隐私约束：服务端不落盘原图、不留存人脸；仅持久化 SQLite 元数据 + Chroma 文案向量。

---

## 一、部署架构

```
浏览器 (HTTPS)
   │
   ├── 前端静态站（Vercel / Cloudflare Pages / 腾讯云 COS）── dist/
   │        └── 反向代理 /api/* → 后端网关
   │
   └── 后端（容器：Docker / 云函数）── Uvicorn :8000
              ├── SQLite  volume:/app/data/wenzhang.db
              ├── Chroma   volume:/app/data/chroma/
              └── DashScope API（通义千问 VL，主） / GLM-4V（备）
```

## 二、前端部署

```bash
cd frontend
npm ci
npm run build        # 产物在 dist/
```

**托管选择（任选）**

| 平台 | 方式 | 备注 |
|---|---|---|
| Vercel | 导入仓库，Build `npm run build`，Output `dist` | 自带 HTTPS |
| Cloudflare Pages | 同上 | 自带 HTTPS |
| 腾讯云 COS/OSS | `dist/` 上传为静态网站，绑定 CDN 域名 | 需配 HTTPS 证书 |
| 阿里云 OSS + CDN | 同上 | 国内直连更快 |

**API 代理**：生产环境前端域名下将 `/api/*` 反代到后端：
- Vercel：`vercel.json` 配置 rewrites
- Nginx：`location /api/ { proxy_pass http://backend:8000; }`

> 开发联调：Vite dev server 已内置 `/api` → `http://127.0.0.1:8000` 代理。

## 三、后端部署

### 3.1 环境变量（必须）

| 变量 | 必填 | 说明 |
|---|---|---|
| `DASHSCOPE_API_KEY` | 生产必填 | 通义千问 VL（主）。**不配置则回退演示文案** |
| `GLM_API_KEY` | 可选 | 智谱 GLM-4V（备，主失败兜底） |
| `CHROMA_PERSIST_DIR` | 可选 | Chroma 持久化目录，默认 `backend/data/chroma` |

### 3.2 Docker 方式

```bash
cd backend
docker build -t wenzhang-dazi-api .
docker run -d \
  --name wenzhang-api \
  -p 8000:8000 \
  -e DASHSCOPE_API_KEY=你的key \
  -v wenzhang-data:/app/data \
  wenzhang-dazi-api
```

- `wenzhang-data` 卷持久化 SQLite + Chroma（**不含任何图片**）。
- 健康检查：`curl https://你的域名/api/health` → `{"status":"ok","mock":false}`

### 3.3 云函数 / 容器服务

- 腾讯云 Serverless / 阿里云 FC：挂载容器镜像，环境变量同上，配置 HTTP 触发器。
- 内存建议 ≥ 512MB（Chroma 加载 embedding 模型需要）。

## 四、HTTPS 与安全

- 全链路 HTTPS（托管平台默认或 Nginx 配证书）。
- **API Key 只存后端环境变量**，前端不暴露密钥（`apiClient` 只调自有 `/api/*`）。
- CORS：生产需把前端域名加入 `backend/app/__init__.py` 的 `allow_origins`。

## 五、隐私合规清单（上线前自检）

- [ ] 服务端磁盘无原图落盘（图片仅内存转发给模型）
- [ ] Chroma 仅存文案文本向量，无图片/人脸元数据
- [ ] 日志不打图片 base64 / 人脸信息
- [ ] 前端 localStorage 仅存 device_id / 收藏文本 / 草稿
- [ ] 提供"清空历史"入口（收藏页「清空收藏」）
- [ ] 隐私授权流程：首次上传前明确告知"仅用于本次生成"

## 六、性能基线（验收）

| 指标 | 目标 | 说明 |
|---|---|---|
| 首屏加载 | < 2s | 前端静态资源 gzip（当前主包 ~43KB gzip） |
| 首字输出 | < 2s | 前端打字机效果；真实 SSE 接入后可真正流式 |
| 单次生成完成 | < 5s | `/api/generate` 5s 超时 + mock 兜底 |
| 历史容量 | ≥ 1000 条 | localStorage + Chroma 向量 |

## 七、真实 AI 接入（从演示模式切换到生产）

1. 配置 `DASHSCOPE_API_KEY`。
2. 重启后端 → `/api/health` 的 `mock` 字段变为 `false`。
3. 生成接口走真实 Qwen-VL：图片 → 多模态识别 → 3 风格文案；人设召回继续生效。
4. 润色走真实 LLM：替换 `backend/app/routers/polish.py` 的 `mock_polish` 为模型调用即可（响应结构不变）。

## 八、后续 SSE 流式（可选增强）

- 新增 `POST /api/generate/stream`：SSE 逐 token 输出。
- 前端 `fetch` + `ReadableStream` 逐字渲染（替换当前打字机模拟）。
- 保留 `POST /api/generate` 以维持契约测试。
