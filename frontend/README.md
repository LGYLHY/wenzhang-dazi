# 文案搭子 · 前端

> Vue3 + Vite，纯 CSS 变量驱动设计 Token。M0 脚手架 + M1 识图生成主链路。

## 运行

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物在 dist/
```

联调：Vite 已配置 `/api` → `http://127.0.0.1:8000` 代理。后端按 `backend/README.md` 启动。

## 目录结构

```
frontend/src/
├── main.js                       # 入口
├── App.vue                       # 应用骨架 + 导航 + 错误条 + Toast
├── router.js                     # vue-router（M0 仅启用 /generate）
├── api/
│   ├── client.js                 # fetch 封装 + ApiError + 6s 超时
│   └── generate.js               # /api/generate + /api/emotions
├── stores/
│   ├── toast.js                  # 全局 Toast
│   ├── errorBar.js               # 顶部错误条
│   ├── deviceId.js               # localStorage 随机 device_id（PIPL）
│   └── draft.js                  # 草稿保护
├── components/
│   ├── ResultCard.vue            # 文案结果卡（情绪竖条 + 操作行）
│   ├── TonePills.vue             # 6 语气胶囊（多选）
│   └── ImageUploader.vue         # 上传 + 缩略 + 移除
├── views/
│   ├── GenerateView.vue          # 生成主页（M1）
│   └── PlaceholderView.vue       # M2/M3 占位
└── assets/styles/
    ├── tokens.css                # 设计 Token（与设计文档完全一致）
    ├── layout.css                # 骨架 / 导航 / TabBar
    └── components.css            # 按钮 / 卡片 / 骨架屏 / Toast
```

## 设计 Token 强约束

- **颜色、间距、圆角、阴影** 必须使用 CSS 变量，禁止硬编码。
- 新组件若需要"主按钮/次按钮/卡片/胶囊/Toast"等，直接复用对应 class。
- 情绪色见 `tokens.css` 末段 8 个 `--em-*`，与设计文档 §2.2 一一对应。

## 隐私

- device_id 仅本地存，不上报 PII。
- 图片经 FileReader 转 base64 后**仅用于本次请求**，不落 IndexedDB / localStorage。
- 草稿文本（不含图片）存在 localStorage，离站可被 `clearDraft()` 清空。
