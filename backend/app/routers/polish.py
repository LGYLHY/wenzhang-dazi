"""POST /api/polish · M3 AI 润色
- 真实 AI（qwen-turbo）：按模式真正改写（更文艺 / 更简短 / 加 emoji）
- 未配置 API Key 或调用失败：回退 mock 规则版，保证可用
"""
from __future__ import annotations

import os
import json
import re
from pathlib import Path

from fastapi import APIRouter

from app.schemas import PolishRequest, PolishResponse
from app.errors import BizError, CODE_EMPTY_INPUT


router = APIRouter(tags=["polish"])


def _load_env():
    """读取 backend/.env（与 llm_client 一致），注入 DASHSCOPE_API_KEY"""
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()
QWEN_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
USE_MOCK = not QWEN_API_KEY

# 关键词 → emoji（mock 兜底用）
EMOJI_MAP = [
    ("海", "🌊"), ("火锅", "🍲"), ("奶茶", "🧋"), ("蛋糕", "🍰"),
    ("咖啡", "☕"), ("好吃", "😋"), ("开心", "😊"), ("累", "🥱"),
    ("想", "💭"), ("落日", "🌇"), ("花", "🌸"), ("面", "🍜"),
]

# 各模式的润色指令（多种风格，不限文艺）
MODE_PROMPTS = {
    "更文艺": "把这段文案润色得更文艺、更有意境，保留原意，控制在 40 字以内",
    "更简短": "把这段文案压缩得更简短精炼，保留核心意思，读起来完整通顺，控制在 18 字以内",
    "加 emoji": "在合适位置添加 1-2 个贴合内容的 emoji，保持原意",
    "更幽默": "把这段文案改写得更幽默俏皮、有梗，保留原意，控制在 40 字以内",
    "更治愈": "把这段文案改写得更温暖治愈、给人安慰，保留原意，控制在 40 字以内",
}


def mock_polish(text: str, mode: str) -> str:
    """兜底规则版：不再粗暴截断，尽量保留完整语义"""
    t = text.strip()
    if mode == "更简短":
        # 按标点切句取首句（完整通顺），过长再压缩
        first = re.split(r"[。！？!?；;]", t)[0]
        if len(first) > 18:
            first = first[:18] + "…"
        return first
    if mode == "加 emoji":
        emoji = next((v for k, v in EMOJI_MAP if k in t), "✨")
        return f"{t}{emoji}"
    return f"{t}。要我说，日子滚烫，慢慢来也是一种浪漫。✨"


def llm_polish(text: str, mode: str) -> str:
    """真实 AI 润色（qwen-turbo 纯文本，快且便宜）"""
    import dashscope
    from dashscope import Generation

    instruction = MODE_PROMPTS.get(mode, MODE_PROMPTS["更文艺"])
    resp = Generation.call(
        model="qwen-turbo",
        messages=[
            {
                "role": "system",
                "content": "你是朋友圈文案润色助手。只输出润色后的文案本身，不要解释、不要加引号、不要 markdown、不要序号。",
            },
            {"role": "user", "content": f"{instruction}\n原文：{text}"},
        ],
        timeout=12,
    )
    out = ""
    output = getattr(resp, "output", None) or {}
    if isinstance(output, dict):
        # qwen-turbo 系列：output.text；qwen-vl 系列：output.choices[].message.content
        out = output.get("text") or ""
        if not out:
            choices = output.get("choices") or []
            if choices:
                msg = choices[0].get("message") or {}
                out = msg.get("content") or ""
    out = (out or "").strip().strip('"').strip("'")
    # 去可能的编号/emoji 前缀残留
    out = re.sub(r"^[\s\d\.\-\*、]+", "", out).strip()
    return out or mock_polish(text, mode)


@router.post("/polish", response_model=PolishResponse)
def polish(payload: PolishRequest):
    """AI 润色：更文艺 / 更简短 / 加 emoji"""
    text = payload.text.strip()
    if not text:
        raise BizError(CODE_EMPTY_INPUT, "请先输入要润色的文案")
    try:
        out = mock_polish(text, payload.mode) if USE_MOCK else llm_polish(text, payload.mode)
    except Exception:
        out = mock_polish(text, payload.mode)  # LLM 失败兜底
    return PolishResponse(text=out, mode=payload.mode)
