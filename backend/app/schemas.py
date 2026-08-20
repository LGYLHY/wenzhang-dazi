"""Pydantic 数据模型 + 错误信封"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ===== 入参 =====

ToneName = Literal["文艺", "幽默", "带货", "日常", "治愈", "凡尔赛"]


class GenerateRequest(BaseModel):
    image_base64: Optional[str] = Field(default=None, description="data:image/...;base64,... 可选")
    text: str = Field(default="", max_length=500)
    tones: list[ToneName] = Field(default_factory=list, max_length=6)
    template: Optional[str] = Field(default=None, max_length=20, description="模板 prompt_key，如 food/travel/festival/emotion/promo")
    device_id: str = Field(..., min_length=4, max_length=64)


# 润色风格：不只文艺，支持多种风格改写
PolishMode = Literal["更文艺", "更简短", "加 emoji", "更幽默", "更治愈"]


class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    mode: PolishMode = "更文艺"
    device_id: str = Field(..., min_length=4, max_length=64)


class PersonaUpsertRequest(BaseModel):
    device_id: str
    text: str = Field(..., min_length=1, max_length=500)
    emotion: str = "日常"
    tone: str = "日常"


class PersonaRecallRequest(BaseModel):
    device_id: str
    text: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=8)


# ===== 出参 =====


class CopyItem(BaseModel):
    style: str
    emotion: str
    text: str


class GenerateResponse(BaseModel):
    vibe: str
    copies: list[CopyItem]
    used_persona: bool = False  # 是否注入了人设记忆


class PolishResponse(BaseModel):
    text: str
    mode: str
