"""ChromaDB 客户端：仅存文案文本向量，不含图片/人脸
- MVP 阶段：emb_fn 用本地哈希向量 mock，正式接入替换为真实 embedding。
- 部署时可通过环境变量切换 persist 路径。
"""
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions


PERSIST_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma"
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

COLL_NAME = "persona_copies"

# 默认 embedding（MVP 用内置 default，后续可换 BGE / Qwen Text Embedding）
_default_ef = embedding_functions.DefaultEmbeddingFunction()

_client = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(PERSIST_DIR),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            name=COLL_NAME,
            embedding_function=_default_ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def ensure_chroma():
    """启动时调用：加载/创建 collection"""
    _get_collection()


def upsert_copy(device_id: str, text: str, emotion: str, copy_id: str) -> bool:
    """采纳/编辑后的文案写入向量库
    - 仅存文本：图片/人脸不会进入此 collection
    """
    coll = _get_collection()
    coll.upsert(
        ids=[f"{device_id}:{copy_id}"],
        documents=[text],
        metadatas=[{"device_id": device_id, "emotion": emotion}],
    )
    return True


def recall(device_id: str, query_text: str, top_k: int = 3) -> list[str]:
    """风格召回：从该 device 历史文案中找相似 Top-K，注入 prompt"""
    coll = _get_collection()
    try:
        res = coll.query(
            query_texts=[query_text],
            n_results=top_k,
            where={"device_id": device_id},
        )
    except Exception:
        return []
    docs = res.get("documents") or [[]]
    return [d for d in docs[0] if d][:top_k]
