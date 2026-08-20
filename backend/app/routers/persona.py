"""POST /api/persona/upsert · POST /api/persona/recall · M2 阶段会调用"""
from fastapi import APIRouter

from app.schemas import PersonaUpsertRequest, PersonaRecallRequest
from app.data.chroma_client import upsert_copy, recall


router = APIRouter(tags=["persona"])


@router.post("/upsert")
def persona_upsert(payload: PersonaUpsertRequest):
    """采纳/编辑后的文案写入向量库（仅文本，不含图片/人脸）"""
    copy_id = f"{payload.text[:8]}-{hash(payload.text) & 0xfffff:05x}"
    upsert_copy(payload.device_id, payload.text, payload.emotion, copy_id)
    return {"ok": True, "id": f"{payload.device_id}:{copy_id}"}


@router.post("/recall")
def persona_recall_api(payload: PersonaRecallRequest):
    """召回相似历史 Top-K（作为 few-shot）"""
    docs = recall(payload.device_id, payload.text, payload.top_k)
    return {"examples": docs}
