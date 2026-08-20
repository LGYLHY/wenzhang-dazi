"""SQLite：模板 / 偏好 / 历史文案元数据（不含原图、人脸）"""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "wenzhang.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS templates (
    id           TEXT PRIMARY KEY,
    category     TEXT NOT NULL,
    title        TEXT NOT NULL,
    example      TEXT NOT NULL,
    prompt_key   TEXT NOT NULL,
    icon         TEXT NOT NULL,
    sort_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_preferences (
    device_id    TEXT PRIMARY KEY,
    created_at   INTEGER NOT NULL,
    meta         TEXT   -- JSON: 偏好设置
);

CREATE TABLE IF NOT EXISTS history_meta (
    id           TEXT PRIMARY KEY,
    device_id    TEXT NOT NULL,
    created_at   INTEGER NOT NULL,
    vibe         TEXT,
    payload      TEXT  -- JSON: 原始文案数组（不含图片）
);

CREATE INDEX IF NOT EXISTS idx_hist_device ON history_meta(device_id, created_at DESC);
"""


# ===== 内置模板（MVP 期硬编码，不走后台管理）=====

SEED_TEMPLATES = [
    # id,        category, title,                example(多条以 \n 分隔),                prompt_key,    icon,  order
    ("t1",  "旅行", "说走就走的旅行",
     "周末逃离城市，山风和晚霞都免费。\n出发吧，最美的风景在路上。\n把疲惫留给风，把自由还给自己。",
     "travel", "map",    10),
    ("t2",  "旅行", "海边度假感",
     "海浪、椰林、落日，今天是被治愈的一天。\n海风很轻，时间很慢。\n听海，是最便宜的旅行。",
     "travel", "sun",    11),
    ("t3",  "美食", "探店种草",
     "人均 60 的小馆，招牌牛腩我能连汤喝光。\n私藏小店，分享给会吃的朋友。\n这家店，是舌尖上的一次偏心。",
     "food",   "food",   20),
    ("t4",  "美食", "深夜放毒",
     "减肥第 3 天，还是败给了这碗面。\n深夜放毒，是对这一天最诚实的奖励。\n夜深人静，胃比心更诚实。",
     "food",   "food",   21),
    ("t5",  "情感", "心动瞬间",
     "原来喜欢一个人，是连沉默都舒服。\n心动，是不期而遇的心跳。\n第一眼的喜欢，是最真的喜欢。",
     "emotion","heart", 30),
    ("t6",  "情感", "异地思念",
     "相隔两座城，想念却从不过期。\n异地恋，靠的是爱和距离的较量。\n想你的时候，月亮都很圆。",
     "emotion","heart", 31),
    ("t7",  "节日", "生日祝福",
     "愿新的一岁，所念皆所愿。\n生日快乐，敬这闪闪发光的一年。\n又长大一岁，继续做个温暖的人。",
     "festival","gift", 40),
    ("t8",  "节日", "新年讨彩",
     "辞旧迎新，今年也要热气腾腾。\n新的一年，愿你眼里有光、心里有暖。\n跨过旧年，新篇章写给自己。",
     "festival","gift", 41),
    ("t9",  "带货", "好物推荐",
     "用了 30 天的宝藏单品，闭眼入。\n真心推荐，不踩雷的好物。\n自用回购，亲测好用才分享。",
     "promo",  "tag",   50),
    ("t10", "带货", "店铺开业",
     "新店开业，前 50 名到店有惊喜。\n开业大吉，欢迎来打卡。\n新店第一波福利，不容错过。",
     "promo",  "tag",   51),
    # —— 扩充（每类共 5 条）——
    ("t11", "旅行", "山顶看日出",
     "把黎明交给山顶，把烦恼丢进云海。\n攀到山顶的那一刻，太阳刚好升起。\n早安，世界。",
     "travel", "map",   12),
    ("t12", "旅行", "古镇慢游",
     "青石板、老茶馆，时光在这里打了个盹。\n古镇的猫很慢，时间也很慢。\n在这里，连发呆都很有味道。",
     "travel", "map",   13),
    ("t13", "旅行", "公路自驾",
     "窗外的风景在倒退，自由在前进。\n油表指针转下去，心情却涨上来。\n目的地不重要，路上才重要。",
     "travel", "map",   14),
    ("t14", "美食", "早餐仪式感",
     "一顿热气腾腾的早餐，是今天的小确幸。\n早餐吃好，是最低成本的快乐。\n早起的人，配得上这份热气。",
     "food",   "food",  22),
    ("t15", "美食", "家乡味道",
     "还是家里的那碗面，最治愈。\n走多远，都忘不掉这一口。\n家乡味，是胃最熟悉的乡音。",
     "food",   "food",  23),
    ("t16", "美食", "下午茶时光",
     "咖啡配蛋糕，烦恼减半。\n一杯咖啡，半块蛋糕，下午就圆满了。\n给忙碌按一下暂停键。",
     "food",   "food",  24),
    ("t17", "情感", "恋爱日常",
     "和你一起，做什么都开心。\n最好的爱情，是一起变胖也愿意。\n平凡的日常，因为有你而不凡。",
     "emotion","heart", 32),
    ("t18", "情感", "闺蜜友情",
     "一起笑过的人，比风景更难忘。\n真正的闺蜜，是可以一起笑一起哭的人。\n友情最棒的样子，是有你在。",
     "emotion","heart", 33),
    ("t19", "情感", "治愈自我",
     "先爱自己，再去爱这个世界。\n给自己一点时间，慢慢来。\n治愈自己，是一辈子的功课。",
     "emotion","heart", 34),
    ("t20", "节日", "中秋团圆",
     "月亮很圆，你们都在身边。\n一年一中秋，一月一相思。\n团圆是中秋最甜的馅。",
     "festival","gift", 42),
    ("t21", "节日", "母亲节",
     "你陪我长大，我陪你变老。\n妈妈是世界上最难的工作。\n母亲节，不止今天才想起你。",
     "festival","gift", 43),
    ("t22", "节日", "毕业季",
     "前程似锦，顶峰相见。\n毕业不是结束，是新故事的封面。\n多年后回头看，今天是最好的一天。",
     "festival","gift", 44),
    ("t23", "带货", "新品首发",
     "第一批尝鲜的人，已经真香了。\n新品上架，尝鲜价仅此一波。\n早买早享受，错过等一年。",
     "promo",  "tag",   52),
    ("t24", "带货", "限时特惠",
     "手慢无，这次折扣是真的。\n倒计时，错过等明年。\n限时限价，错过真的会哭。",
     "promo",  "tag",   53),
    ("t25", "带货", "好物测评",
     "用过才敢说好，闭眼入不踩雷。\n亲测好用才推荐。\n一份客观的测评报告，请查收。",
     "promo",  "tag",   54),
    # —— 再扩充（每类共 8 条）——
    ("t26", "旅行", "雨天宅家",
     "窗外下雨，窗内正好煮一壶茶。\n雨天不出门，是给心情放个假。\n雨声是最好的白噪音。",
     "travel", "map",   15),
    ("t27", "旅行", "城市夜景",
     "霓虹与车流，是城市的另一种温柔。\n夜晚的城市比白天更诚实。\n万家灯火，总有一盏是为你。",
     "travel", "map",   16),
    ("t28", "旅行", "露营野餐",
     "帐篷、炭火、星星，今晚睡在自然里。\n露营是成年人的过家家。\n头顶没有天花板，就是最贵的房。",
     "travel", "map",   17),
    ("t29", "美食", "周末大餐",
     "周末的仪式感，是一顿认真的晚餐。\n不用点外卖，今晚自己做主厨。\n周末，是胃最期待的日子。",
     "food",   "food",  25),
    ("t30", "美食", "甜品治愈",
     "不开心的时候，糖分是最好的解药。\n甜品不吃不行，这是身体的需要。\n一口甜，治愈所有不愉快。",
     "food",   "food",  26),
    ("t31", "美食", "街头小吃",
     "巷子口的小吃摊，藏着最朴实的快乐。\n烟火气最浓的地方，是小吃摊。\n街边的小吃，永远不会让你失望。",
     "food",   "food",  27),
    ("t32", "情感", "亲情陪伴",
     "一家人整整齐齐，就是最好的时光。\n陪伴是最长情的告白。\n回家吃饭，是最暖的召唤。",
     "emotion","heart", 35),
    ("t33", "情感", "职场同事",
     "并肩作战的日子，是青春里闪光的章节。\n和对的人一起加班，也能加班出快乐。\n同事变挚友，是最大的彩蛋。",
     "emotion","heart", 36),
    ("t34", "情感", "告别时刻",
     "离别是为了更好的重逢。\n好好告别，是为了好好记住。\n笑着说再见，是因为相信会再见。",
     "emotion","heart", 37),
    ("t35", "节日", "七夕告白",
     "星河滚烫，你是人间理想。\n七夕快乐，致最想见的人。\n爱情最好的样子，是一起变老。",
     "festival","gift", 45),
    ("t36", "节日", "国庆假期",
     "愿山河无恙，人间皆安。\n假期很短，故事很长。\n国庆的快乐，从放下手机开始。",
     "festival","gift", 46),
    ("t37", "节日", "腊八暖冬",
     "一碗热粥，就是冬天最实在的温暖。\n腊八到，年味近，粥先暖。\n寒冷的冬日，从一碗粥开始。",
     "festival","gift", 47),
    ("t38", "带货", "穿搭分享",
     "今日 OOTD：舒适与好看，我都要。\n今天的穿搭是给心情加的滤镜。\n穿什么，就是想成为什么。",
     "promo",  "tag",   55),
    ("t39", "带货", "零食测评",
     "追剧伴侣已就位，零食储备已上线。\n深夜零食测评，附热量警告。\n快乐可以很简单，一包零食的事。",
     "promo",  "tag",   56),
    ("t40", "带货", "家居好物",
     "换个小物件，家的幸福感立刻提升。\n家居改造，从一件小物开始。\n好的家居，是给生活加分。",
     "promo",  "tag",   57),
]


def init_db():
    """初始化表结构；模板为静态数据，每次启动重灌（幂等）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        cur = conn.cursor()
        cur.execute("DELETE FROM templates")
        cur.executemany(
            "INSERT INTO templates(id, category, title, example, prompt_key, icon, sort_order) VALUES (?,?,?,?,?,?,?)",
            SEED_TEMPLATES,
        )
        conn.commit()


@contextmanager
def get_conn():
    """简洁的连接获取：with get_conn() as c: c.execute(...)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
