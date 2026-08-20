"""Prompt 拼装：把 persona 召回结果注入 system prompt"""
from __future__ import annotations


SYSTEM_PROMPT = (
    "你是一名'朋友圈文案搭子'，请基于用户的图片/心情，输出 JSON："
    '{ "vibe": string, "copies": [ { "style": string, "emotion": string, "text": string } ] }'
    " - style 取自用户给出的语气集合"
    " - 3 条文案必须风格差异明显，避免雷同"
    " - 单条长度 12–60 字，避免过度堆砌 emoji"
)


def build_user_payload(
    *,
    user_text: str,
    tones: list[str],
    template_key: str | None,
    persona_examples: list[str],
) -> str:
    parts = [f"用户心情：{user_text or '（未提供）'}"]
    parts.append(f"语气：{'、'.join(tones) or '不限'}")
    if template_key:
        parts.append(f"模板：{template_key}")
    if persona_examples:
        parts.append(
            "历史采纳风格参考（few-shot，请贴近但不要复制）："
            + " | ".join(f"《{t}》" for t in persona_examples)
        )
    parts.append("请严格输出 JSON，不要额外解释。")
    return "\n".join(parts)
