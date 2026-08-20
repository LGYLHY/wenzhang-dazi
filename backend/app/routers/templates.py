"""GET /api/templates · M3 模板广场"""
from fastapi import APIRouter, Query
from app.data.db import get_conn


router = APIRouter(tags=["templates"])


@router.get("/templates")
def list_templates(category: str = Query(default="all")):
    """返回模板列表；example 字段为多行示例（数组），方便前端展示多条。
    category=all|festival|travel|food|emotion|promo
    """
    sql = "SELECT id, category, title, example, prompt_key, icon FROM templates"
    params = ()
    if category and category != "all":
        sql += " WHERE category = ?"
        params = (category,)
    sql += " ORDER BY sort_order ASC, id ASC"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    result = []
    for r in rows:
        item = dict(r)
        raw = item.get("example") or ""
        if raw:
            items = [ex for ex in raw.split("\n") if ex.strip()]
            item["example"] = items if items else [raw]
        else:
            item["example"] = []
        result.append(item)
    return result