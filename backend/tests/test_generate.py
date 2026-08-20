"""M0+M1 阶段自动化契约测试：覆盖 /api/generate 的输入/输出/错误信封。"""
import io
import base64
import pytest
from fastapi.testclient import TestClient

from app import app
from app.data.db import init_db, DB_PATH
from app.data.chroma_client import ensure_chroma


@pytest.fixture(scope="session", autouse=True)
def _setup():
    init_db()
    ensure_chroma()


@pytest.fixture()
def client():
    return TestClient(app)


def _device():
    return "test-device-001"


def _b64_jpeg():
    """构造一个 1x1 合法 jpg 的 base64，避免传真实图片"""
    data = base64.b64decode(
        b"/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"
        b"HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy"
        b"MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAEAAQADASIA"
        b"AhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEB"
        b"AAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AB//Z"
    )
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


# ===== AC1 合法图片生成 =====

def test_ac1_valid_text_only(client):
    """未传图、但有文字：也应能生成"""
    resp = client.post("/api/generate", json={
        "text": "今天去了海边",
        "tones": ["文艺", "治愈"],
        "device_id": _device(),
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "vibe" in data and data["vibe"]
    assert 3 <= len(data["copies"]) <= 5
    for c in data["copies"]:
        assert {"style", "emotion", "text"} <= set(c.keys())
        assert c["text"]


def test_ac1_valid_image_and_text(client):
    resp = client.post("/api/generate", json={
        "image_base64": _b64_jpeg(),
        "text": "在海边拍的",
        "tones": ["文艺"],
        "device_id": _device(),
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["copies"]) >= 1


# ===== AC3 空提交 =====

def test_ac3_empty_input_rejected(client):
    resp = client.post("/api/generate", json={
        "text": "",
        "tones": [],
        "device_id": _device(),
    })
    assert resp.status_code == 422  # BizError -> 422
    detail = resp.json()["detail"]
    assert detail["code"] == "EMPTY_INPUT"


# ===== AC2 格式/大小不符 =====

def test_ac2_invalid_image_format_rejected(client):
    resp = client.post("/api/generate", json={
        "image_base64": "data:image/gif;base64,abcdef",
        "text": "x",
        "tones": [],
        "device_id": _device(),
    })
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "INVALID_IMAGE"


# ===== 错误信封与基础字段 =====

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_emotions(client):
    resp = client.get("/api/emotions")
    assert resp.status_code == 200
    data = resp.json()
    assert "文艺" in data and "日常" in data


def test_templates_default(client):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) >= 8
    cats = {it["category"] for it in items}
    assert {"旅行", "美食", "节日", "情感", "带货"} <= cats


def test_templates_by_category(client):
    resp = client.get("/api/templates", params={"category": "美食"})
    assert resp.status_code == 200
    items = resp.json()
    assert items and all(it["category"] == "美食" for it in items)


# ===== M2 接口占位 =====

def test_persona_upsert_and_recall(client):
    # upsert
    resp = client.post("/api/persona/upsert", json={
        "device_id": _device(),
        "text": "海风把烦恼吹散了。",
        "emotion": "治愈",
        "tone": "文艺",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    # recall
    resp = client.post("/api/persona/recall", json={
        "device_id": _device(),
        "text": "海边",
        "top_k": 3,
    })
    assert resp.status_code == 200
    examples = resp.json()["examples"]
    assert isinstance(examples, list)
