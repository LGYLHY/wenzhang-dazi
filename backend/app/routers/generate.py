"""POST /api/generate · M1 核心：识图 + 风格生成"""
from __future__ import annotations

import re
import time
import uuid
import asyncio
import base64
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas import GenerateRequest, GenerateResponse, CopyItem
from app.errors import BizError, CODE_EMPTY_INPUT, CODE_INVALID_IMG, CODE_RECOG_FAIL, CODE_MODEL_TIMEOUT
from app.services.llm_client import call_qwen_vl, EMOTION_COLORS
from app.services.prompt_builder import build_user_payload
from app.data.chroma_client import recall as persona_recall


router = APIRouter(tags=["generate"])

# ===== 配置 =====
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_IMG_REGEX = re.compile(r"^data:image/(jpeg|jpg|png|webp);base64,(.+)$", re.I)
GENERATE_TIMEOUT_S = 15.0  # 真实 LLM 生成 3 条文案的合理等待（mock 下远快于此）
# 朴素限流：单 device 30 秒内最多 10 次（演示/分享场景友好）
_RATE_BUCKET: dict[str, list[float]] = {}
RATE_WINDOW_S = 30
RATE_LIMIT = 10


def _check_rate(device_id: str):
    now = time.time()
    bucket = [t for t in _RATE_BUCKET.get(device_id, []) if now - t < RATE_WINDOW_S]
    if len(bucket) >= RATE_LIMIT:
        raise BizError("RATE_LIMIT", f"操作过于频繁，请 {RATE_WINDOW_S}s 后再试", http_status=429)
    bucket.append(now)
    _RATE_BUCKET[device_id] = bucket


def _validate_image_b64(b64: str | None) -> str | None:
    """校验 data:image/(jpeg|jpg|png|webp);base64,... 且长度 ≤ 10MB 还原后大小"""
    if not b64:
        return None
    m = ALLOWED_IMG_REGEX.match(b64.strip())
    if not m:
        raise BizError(CODE_INVALID_IMG, "仅支持 JPG/PNG/WEBP 图片", http_status=422)
    try:
        raw = base64.b64decode(m.group(2), validate=True)
    except Exception:
        raise BizError(CODE_INVALID_IMG, "图片编码不合法")
    if len(raw) > MAX_IMAGE_BYTES:
        raise BizError(CODE_INVALID_IMG, "图片超过 10MB，请压缩后重试")
    return b64


@router.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest):
    """M1 主链路：
    1. 限流 2. 输入校验（图/文至少其一）3. persona 召回
    4. 调 LLM（带 5s 超时）5. JSON 解析兜底
    """
    _check_rate(payload.device_id)
    image = _validate_image_b64(payload.image_base64)

    if not image and not payload.text.strip():
        raise BizError(CODE_EMPTY_INPUT, "请先上传图片或写一句话")

    # 召回该用户的文案风格，作为 few-shot
    examples = persona_recall(payload.device_id, payload.text or "心情", top_k=3)

    try:
        # 跑在 asyncio 线程池里，并把超时交由外部包装
        result = await asyncio.wait_for(
            asyncio.to_thread(
                call_qwen_vl,
                image,
                payload.text,
                payload.tones,
                payload.template,
                examples,
                GENERATE_TIMEOUT_S,
                payload.swap_text,
            ),
            timeout=GENERATE_TIMEOUT_S + 1.0,
        )
    except asyncio.TimeoutError:
        raise BizError(CODE_MODEL_TIMEOUT, "生成超时，请重试", http_status=504)

    # 兜底字段
    copies_raw = result.get("copies") or []
    if not copies_raw:
        raise BizError(CODE_RECOG_FAIL, "未能识别有效内容，请换一张更清晰的图或补充文字", http_status=422)

    copies = [CopyItem(style=c["style"], emotion=c["emotion"], text=c["text"]) for c in copies_raw]

    return GenerateResponse(
        vibe=result.get("vibe") or copies[0].emotion,
        copies=copies,
        used_persona=bool(examples),
    )


@router.get("/emotions")
def list_emotions():
    """暴露给前端调色板用"""
    return EMOTION_COLORS
