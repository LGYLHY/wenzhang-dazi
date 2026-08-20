"""LLM 客户端：主用通义千问 VL（DashScope），备用 GLM-4V。
MVP 阶段若未配置 API Key，则走本地 mock（保闭环可演示）。

隐私：image_base64 通过 SDK 临时发送给模型，**不在本服务落盘**。
"""
from __future__ import annotations

import os
import json
import random
import base64
import re
import time
from pathlib import Path
from typing import Any


def _load_env_file():
    """读取 backend/.env（若存在），把 DASHSCOPE_API_KEY / GLM_API_KEY 注入环境变量。
    避免把 Key 写进代码或对话日志，重启后端即生效。
    """
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

QWEN_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
USE_MOCK = not QWEN_API_KEY  # 无 key 一律 mock，开发环境可演示


# ====== 调色（与设计文档 8 色情绪一一对应）======
EMOTION_COLORS = {
    "日常": "#E8590C",
    "治愈": "#0D9488",
    "幽默": "#FFB703",
    "文艺": "#7F77DD",
    "带货": "#A8763E",
    "凡尔赛": "#378ADD",
    "清新": "#5DCAA5",
    "情感": "#F2708A",
}


# ====== Mock 文案池：保证每个请求 3 条不同风格，每个主题分类 ≥6 条
# （确保滑动窗口排除最近 6 条后仍有 ≥3 条可选，避免二次生成重复）
MOCK_COPIES = [
    # —— 海边/旅行 ——
    ("文艺", "清新", "海风把我吹得有点恍惚，今天的云比昨天更慢一些。"),
    ("治愈", "清新", "坐了一下午，海把烦恼卷走了，留下温柔。"),
    ("幽默", "清新", "海边散步的认真程度，取决于手机还剩多少电。"),
    ("凡尔赛", "情感", "也不是刻意浪漫，只是恰好赶上了这场日落。"),
    ("清新", "清新", "下一站不是远方，是有你在的每一站。"),
    ("治愈", "清新", "海浪一遍遍刷着沙滩，好像想把我的烦恼也一起带走。"),
    ("文艺", "清新", "赤脚走在海浪边的沙滩上，时间好像变慢了。"),
    # —— 美食 ——
    ("带货", "清新", "今日小确幸：一杯奶茶，三分糖，去冰，刚好。"),
    ("带货", "日常", "本地人私藏的小馆，人均 60，招牌牛腩连汤都能喝光。"),
    ("幽默", "日常", "KPI 还没影，奶茶先续上了，打工人的快乐就这么简单。"),
    ("治愈", "情感", "火锅咕嘟咕嘟冒着泡，比任何情话都治愈。"),
    ("带货", "日常", "甜品店新出的蛋糕，甜过初恋，值得绕路打卡。"),
    ("幽默", "日常", "体重秤它不懂，我吃的火锅里全是快乐。"),
    ("治愈", "情感", "深夜泡面加个蛋，再来杯奶茶，就是普通日子的高光时刻。"),
    # —— 加班/打工人 ——
    ("幽默", "日常", "今天也是和困意正面交锋的一天，险胜。"),
    ("幽默", "日常", "别人晒图是氛围感，我晒图是日常摆烂合集。"),
    ("文艺", "情感", "今晚的月色真美，适合熬夜，也适合想早睡的你。"),
    ("幽默", "日常", "嘴上说着躺平，身体却很诚实地打开了电脑。"),
    ("文艺", "情感", "凌晨的城市安静得像一张白纸，我的工位是唯一没合上的笔帽。"),
    # —— 情感/想念 ——
    ("情感", "情感", "隔着屏幕笑出声的次数，正在无限逼近见面那天。"),
    ("文艺", "情感", "喜欢一个人，是连沉默都舒服。"),
    ("治愈", "情感", "傍晚的风软软的，像有人轻轻拍了拍你的肩膀说：辛苦了。"),
    ("文艺", "情感", "遇见你之后，连喜欢都变得理直气壮了。"),
    ("日常", "情感", "想念是一道填空题，答案全是你的名字。"),
    # —— 治愈/文艺 ——
    ("文艺", "日常", "把心事写进窗边的光里，影子替我签收。"),
    ("治愈", "日常", "允许自己慢一点，也是一种勇敢。"),
    ("凡尔赛", "日常", "随手拍的一张，朋友说我太会享受，其实只是恰好路过。"),
    ("文艺", "情感", "黄昏把天边染成橘子汽水，想说的话都泡在晚风里。"),
    ("清新", "清新", "路过一棵开花的树，停下来看了很久，没人催我。"),
    ("日常", "治愈", "今天没做什么大事，但感觉被生活认真爱了一遍。"),
    ("文艺", "清新", "生活偶尔按下暂停键，是为了让温柔跟上。"),
    ("日常", "治愈", "把今天过好，就是给明天最好的礼物。"),
    # —— 海边/旅行（扩充）——
    ("清新", "清新", "涨潮时捡到的贝壳，每一片都装着大海的小秘密。"),
    ("治愈", "清新", "看海浪一遍遍涨退，突然觉得什么事都能翻篇。"),
    # —— 美食（扩充）——
    ("带货", "日常", "这家店的招牌牛腩我一周来三次，每次都把汤喝光。"),
    ("幽默", "日常", "减肥路上的绊脚石，往往是深夜那杯三分糖的奶茶。"),
    # —— 加班/打工人（扩充）——
    ("幽默", "日常", "老板画的饼，够我加班到明年。"),
    ("文艺", "情感", "加班的夜里，工位很安静，只有键盘声在替我说加油。"),
    ("日常", "治愈", "下班到家泡了个热水澡，一天的累都被冲走了。"),
    # —— 情感/想念（扩充）——
    ("文艺", "情感", "所有的怦然心动，都藏在没说出的话里。"),
    ("日常", "情感", "想念的时候，就翻翻我们的聊天记录。"),
    ("治愈", "情感", "异地恋最浪漫的事，是每次见面都像第一次心动。"),
    # —— 治愈/文艺（扩充）——
    ("文艺", "清新", "把生活调成静音模式，听风、听雨、听自己。"),
    ("日常", "治愈", "今天的自己有点辛苦，记得奖励自己一朵小花。"),
    # —— 美食（扩充 2）——
    ("带货", "清新", "夏天第一口冰奶茶，比恋爱还甜。"),
    ("治愈", "日常", "深夜的一碗泡面，是治愈一切的魔法。"),
    ("幽默", "情感", "对甜品的抵抗力为负，对好心情的抵抗力也为负。"),
    # —— 海边/旅行（扩充 2）——
    ("清新", "清新", "海风吹过的夏天，连汽水都变甜了。"),
    ("文艺", "清新", "把黄昏寄给你，附上一整片海。"),
    ("治愈", "清新", "看海的人，眼里装得下星辰。"),
    # —— 加班/打工人（扩充 2）——
    ("幽默", "日常", "工作群里@我，我就知道今天的快乐到此为止。"),
    ("文艺", "日常", "凌晨两点，外卖小哥和代码一样努力。"),
    ("日常", "治愈", "下班路上的晚风，是打工人免费的犒赏。"),
    ("幽默", "日常", "今天的工作清单：睡觉、喝水、假装很忙。"),
    # —— 情感/想念（扩充 2）——
    ("文艺", "情感", "喜欢你之后，连日常都变得有光。"),
    ("治愈", "情感", "慢慢来，谁不是翻山越岭去喜欢一个人。"),
    ("日常", "情感", "想念的每一天，都在为下一次见面蓄力。"),
    ("幽默", "情感", "异地恋的浪漫：把想念说成今天的月亮很圆。"),
    # —— 治愈/文艺（扩充 2）——
    ("文艺", "清新", "日子是庸常的，但温柔的人会把光洒进来。"),
    ("清新", "清新", "桂花落了一地，秋天好温柔。"),
    ("治愈", "日常", "累了就慢下来，看看云，喝口水，再出发。"),
    ("日常", "治愈", "给自己买了一束花，庆祝平凡的一天。"),
]

# 关键词 → 文案池中的匹配子串（输入联想，让 mock 更贴近"输入什么出什么"）
KEYWORD_RULES: list[tuple[list[str], list[str]]] = [
    (["海", "海边", "沙滩", "海风", "度假", "日落", "旅行", "旅游"],
     ["海", "海边", "日落", "远方"]),
    (["火锅", "吃", "美食", "奶茶", "咖啡", "探店", "甜品", "牛腩", "蛋糕", "泡面", "吃饱"],
     ["奶茶", "牛腩", "火锅", "甜品", "蛋糕", "小馆", "泡面"]),
    (["加班", "工作", "打工", "累", "困", "KPI", "通勤", "熬夜", "躺平", "凌晨", "下班"],
     ["困意", "摆烂", "KPI", "熬夜", "躺平", "凌晨", "加班", "累", "下班", "打工人", "工作"]),
    (["想你", "想念", "恋爱", "心动", "喜欢", "异地", "约会", "想她", "想他", "想", "遇见"],
     ["隔着屏幕", "喜欢", "想念", "远方", "傍晚的风", "心动", "异地"]),
    (["黄昏", "晚风", "云", "花", "树", "安静", "慢", "温柔", "礼物", "风"],
     ["黄昏", "晚风", "开花的树", "慢一点", "温柔", "礼物", "花", "风"]),
]

# 最近用过的文案（滑动窗口，避免相邻轮次重复）
_used_texts: list[str] = []
_USED_WINDOW = 6
# 全历史已用文案（整池用尽才重置，保证长轮次也不重复）
_ever_used: set[str] = set()


def _keyword_pool(text: str, template_key: str | None) -> list[tuple[str, str, str]] | None:
    """根据输入文本 + 模板 key 从文案池中挑出语义相关的候选；无匹配返回 None"""
    # 模板优先：food → 美食池；travel → 旅行/海边池；其余走输入联想
    if template_key == "food":
        return [c for c in MOCK_COPIES if any(k in c[2] for k in ("奶茶", "牛腩", "火锅", "甜品", "蛋糕", "小馆"))]
    if template_key == "travel":
        return [c for c in MOCK_COPIES if any(k in c[2] for k in ("海", "海边", "日落", "远方"))]

    if not text:
        return None
    for keywords, keys in KEYWORD_RULES:
        if any(k in text for k in keywords):
            matched = [c for c in MOCK_COPIES if any(k in c[2] for k in keys)]
            if len(matched) >= 3:
                return matched
    return None


def _mock_pick(text: str, tones: list[str], vibe_hint: str | None, template_key: str | None, swap_text: str | None = None) -> dict[str, Any]:
    """按模板/输入联想 + 用户选择语气挑 3 条。
    去重策略：全历史去重（_ever_used），分类池用尽后混入全池，
    保证连续生成多轮不出现完全相同的文案。
    swap_text：换一条时传入的当前文案，强制从候选中排除，避免"换了个寂寞"。
    """
    global _used_texts, _ever_used
    pool = _keyword_pool(text, template_key) or list(MOCK_COPIES)
    if swap_text:
        pool = [c for c in pool if c[2] != swap_text]
    if tones:
        # 联想池按语气过滤；不足 3 条则回退到全池按语气过滤；再不足则全池
        tone_pool = [c for c in pool if c[0] in tones]
        if len(tone_pool) >= 3:
            pool = tone_pool
        else:
            full_tone = [c for c in MOCK_COPIES if c[0] in tones] or MOCK_COPIES
            pool = full_tone if len(full_tone) >= 3 else MOCK_COPIES

    # 候选：联想池优先"从未用过"的
    unused_in_pool = [c for c in pool if c[2] not in _ever_used]
    if len(unused_in_pool) >= 3:
        candidates = unused_in_pool
    else:
        # 主题池用尽：在同一主题池内轮换（保持主题相关性，不跑偏到其他主题）
        # 用 min-overlap 思路：从主题池随机抽 3 条，尽量与最近用过的少重复
        used_recent = set(_used_texts[-_USED_WINDOW:])
        best, best_overlap = None, None
        for _ in range(30):
            cand = random.sample(pool, k=3)
            overlap = sum(1 for t in cand if t[2] in used_recent)
            if best_overlap is None or overlap < best_overlap:
                best, best_overlap = cand, overlap
                if overlap == 0:
                    break
        candidates = best or pool[:3]
        _ever_used = set()  # 进入轮换即视为一轮结束，重置全局去重

    picks = random.sample(candidates, k=3)
    _used_texts = (_used_texts + [t for _, _, t in picks])[-_USED_WINDOW:]
    _ever_used.update(t for _, _, t in picks)

    copies = [
        {"style": s, "emotion": e, "text": t}
        for s, e, t in picks
    ]
    return {
        "vibe": vibe_hint or picks[0][1],
        "copies": copies,
    }


def call_qwen_vl(
    image_b64: str | None,
    text: str,
    tones: list[str],
    template_key: str | None,
    persona_examples: list[str],
    timeout_s: float = 5.0,
    swap_text: str | None = None,
) -> dict[str, Any]:
    """调用 Qwen-VL；超时/未配置走 mock。

    返回：{"vibe": str, "copies": [{"style","emotion","text"} ...]}
    swap_text：换一条时传入，要求新内容不与它重复。
    """
    if USE_MOCK:
        # mock 路径下模拟一点点耗时，但确保 <5s
        time.sleep(min(0.6, timeout_s / 8))
        return _mock_pick(text, tones, None, template_key, swap_text)

    # ===== 真实接口路径（示意 + 安全护栏）=====
    try:
        import dashscope  # type: ignore
        from dashscope import MultiModalConversation  # type: ignore

        messages = _build_messages(image_b64, text, tones, template_key, persona_examples, swap_text)
        resp = MultiModalConversation.call(
            model="qwen-vl-plus",
            messages=messages,
            timeout=timeout_s,
        )
        result = _parse_qwen(resp)
        # 真实 AI 可能少给：不足 3 条时用 mock 池补充，保证体验一致
        copies = result.get("copies") or []
        if len(copies) < 3:
            extra = _mock_pick(text, tones, None, template_key, swap_text)["copies"]
            used = {c["text"] for c in copies}
            result["copies"] = copies + [c for c in extra if c["text"] not in used][: 3 - len(copies)]
        # 若仍包含 swap_text，剔除它（极端兜底，避免"换了个寂寞"）
        if swap_text:
            result["copies"] = [c for c in result["copies"] if c["text"] != swap_text][:3]
        return result
    except Exception as exc:  # noqa: BLE001
        # 兜底走 mock，不让用户白屏
        return _mock_pick(text, tones, None, template_key, swap_text)


def _build_messages(image_b64, text, tones, template_key, persona_examples, swap_text=None):
    """组装多模态 messages（真实接口路径）"""
    sys = (
        "你是\"朋友圈文案搭子\"，根据用户的输入生成 3 条不同风格的中文朋友圈文案。\n"
        "严格只输出一个 JSON 对象，不要输出任何其他文字、序号、markdown、emoji 或 hashtag：\n"
        '{"vibe": "整体情绪", "copies": [{"style": "文艺", "emotion": "清新", "text": "文案内容"}]}\n'
        "要求：\n"
        "- 每条文案 12~60 字，口语化、有画面感，可直接复制发朋友圈\n"
        "- 必须恰好输出 3 条 copies（不多不少）\n"
        "- 3 条 style 互不相同，从 文艺/幽默/治愈/带货/日常/凡尔赛/清新/情感 中选择\n"
        '- emotion 必须是 日常/治愈/幽默/文艺/带货/凡尔赛/清新/情感 之一'
    )
    user_content = []
    if image_b64:
        # 去掉 data:image/...;base64, 前缀
        b64 = re.sub(r"^data:image/\w+;base64,", "", image_b64)
        user_content.append({"image": f"data:image/jpeg;base64,{b64}"})
    user_text = f"心情：{text}\n语气：{tones}\n模板：{template_key}\n历史风格参考：{persona_examples}"
    if swap_text:
        user_text += (
            "\n【换一条】下面这条是用户想替换掉的，新生成的 3 条里"
            "严禁与之雷同或仅改几个字，请换全新的角度与表达："
            f"「{swap_text}」"
        )
    user_content.append({"text": user_text})
    return [{"role": "system", "content": [{"text": sys}]}, {"role": "user", "content": user_content}]


def _parse_qwen(resp) -> dict[str, Any]:
    """从 Qwen 输出中解析 JSON；失败时降级按行清洗兜底"""
    try:
        content = resp["output"]["choices"][0]["message"]["content"]
        if isinstance(content, list):
            text = "".join(c.get("text", "") for c in content if isinstance(c, dict))
        else:
            text = str(content)

        # 1) 优先提取 JSON 块
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                data = json.loads(m.group(0))
            except Exception:
                data = {}
            copies = data.get("copies") or []
            copies = [
                {
                    "style": c.get("style", "日常"),
                    "emotion": c.get("emotion", "日常"),
                    "text": (c.get("text") or "").strip()[:140],
                }
                for c in copies
            ][:5]
            if copies:
                return {"vibe": data.get("vibe") or copies[0]["emotion"], "copies": copies}

        # 2) 非 JSON 兜底：按行提取，清洗编号/hashtag/emoji
        parsed: list[dict[str, str]] = []
        for line in text.splitlines():
            clean = re.sub(r"^[\s\d\.\-\*、]+", "", line.strip())  # 去序号
            clean = re.sub(r"[#＃][^\s#＃]+", "", clean)  # 去 hashtag
            clean = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]", "", clean)  # 去 emoji
            clean = clean.strip(' "\'*【】')
            if 6 <= len(clean) <= 100:
                parsed.append({"style": "日常", "emotion": "日常", "text": clean[:140]})
            if len(parsed) >= 5:
                break
        if parsed:
            return {"vibe": "日常", "copies": parsed}

        return _mock_pick("", [], None, None)
    except Exception:
        return _mock_pick("", [], None, None)
