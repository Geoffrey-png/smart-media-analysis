import math
import re
from datetime import datetime

try:
    import jieba
    import jieba.analyse
except Exception:  # pragma: no cover
    jieba = None


CATEGORY_KEYWORDS = {
    "科技": [
        "人工智能",
        "AI",
        "算法",
        "机器学习",
        "芯片",
        "互联网",
        "软件",
        "数据",
        "大模型",
        "云计算",
        "数字化",
        "technology",
        "tech",
        "software",
        "chip",
        "semiconductor",
        "robot",
    ],
    "财经": [
        "股票",
        "市场",
        "企业",
        "投资",
        "经济",
        "金融",
        "消费",
        "银行",
        "基金",
        "上市",
        "产业",
        "business",
        "economy",
        "market",
        "finance",
        "investment",
        "company",
    ],
    "体育": [
        "比赛",
        "球星",
        "冠军",
        "赛事",
        "运动员",
        "联赛",
        "足球",
        "篮球",
        "训练",
        "积分",
        "sport",
        "football",
        "basketball",
        "league",
    ],
    "娱乐": [
        "电影",
        "音乐",
        "明星",
        "综艺",
        "票房",
        "导演",
        "演唱会",
        "剧集",
        "节目",
        "film",
        "movie",
        "music",
        "celebrity",
    ],
    "社会": [
        "城市",
        "民生",
        "教育",
        "医疗",
        "交通",
        "社区",
        "就业",
        "养老",
        "公共服务",
        "society",
        "education",
        "healthcare",
        "city",
    ],
    "文化": ["文化", "旅游", "非遗", "阅读", "博物馆", "展览", "艺术", "文创", "culture", "travel", "museum", "art"],
    "国际": [
        "国际",
        "全球",
        "外交",
        "海外",
        "贸易",
        "联合国",
        "地区局势",
        "world",
        "global",
        "foreign",
        "war",
        "government",
    ],
    "健康": ["健康", "医疗", "医院", "医生", "疾病", "营养", "运动", "心理", "health", "medical", "doctor", "disease"],
}

POSITIVE_WORDS = {
    "增长",
    "提升",
    "突破",
    "创新",
    "优秀",
    "成功",
    "改善",
    "高效",
    "领先",
    "利好",
    "稳定",
    "升级",
    "growth",
    "success",
    "improve",
    "breakthrough",
}

NEGATIVE_WORDS = {
    "下降",
    "风险",
    "冲突",
    "问题",
    "失败",
    "违规",
    "低迷",
    "事故",
    "投诉",
    "压力",
    "损失",
    "下滑",
    "risk",
    "conflict",
    "crisis",
    "loss",
    "decline",
}

SENSITIVE_WORDS = {"暴力", "诈骗", "谣言", "赌博", "违法", "涉黄", "恐怖", "极端"}


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _split_words(text: str) -> list[str]:
    text = _clean_text(text)
    if not text:
        return []
    if jieba:
        words = [w.strip() for w in jieba.lcut(text) if len(w.strip()) > 1]
    else:
        words = re.findall(r"[\u4e00-\u9fa5A-Za-z0-9]{2,}", text)
    stop_words = {"一个", "我们", "他们", "以及", "通过", "进行", "已经", "同时", "相关", "记者", "表示", "the", "and", "for", "with"}
    return [w for w in words if w.lower() not in stop_words]


def extract_keywords(title: str, content: str, top_k: int = 8) -> list[str]:
    text = f"{title or ''} {content or ''}"
    if not text.strip():
        return []
    if jieba:
        return [item for item in jieba.analyse.extract_tags(text, topK=top_k) if item.strip()]

    counts: dict[str, int] = {}
    for word in _split_words(text):
        counts[word] = counts.get(word, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_k]]


def generate_summary(content: str, max_length: int = 160) -> str:
    content = _clean_text(content)
    if not content:
        return ""
    if len(content) <= max_length:
        return content

    sentences = re.split(r"[。！？!?]\s*", content)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return content[:max_length]

    keywords = set(extract_keywords("", content, top_k=10))
    scored = []
    for index, sentence in enumerate(sentences):
        score = sum(1 for kw in keywords if kw in sentence)
        score += max(0, 3 - index) * 0.2
        scored.append((score, index, sentence))
    selected = sorted(sorted(scored, reverse=True)[:3], key=lambda x: x[1])
    summary = "。".join(item[2] for item in selected)
    if len(summary) > max_length:
        summary = summary[:max_length].rstrip("，, ") + "..."
    return summary


def classify_content(title: str, content: str, keywords: list[str] | None = None) -> str:
    text = f"{title or ''} {content or ''} {' '.join(keywords or [])}".lower()
    scores: dict[str, int] = {}
    for category, words in CATEGORY_KEYWORDS.items():
        scores[category] = sum(text.count(word.lower()) for word in words)
    best_category, best_score = max(scores.items(), key=lambda x: x[1])
    return best_category if best_score > 0 else "综合"


def analyze_sentiment(content: str) -> str:
    text = (content or "").lower()
    positive = sum(text.count(word.lower()) for word in POSITIVE_WORDS)
    negative = sum(text.count(word.lower()) for word in NEGATIVE_WORDS)
    if positive - negative >= 2:
        return "positive"
    if negative - positive >= 2:
        return "negative"
    return "neutral"


def detect_sensitive_words(title: str, content: str) -> list[str]:
    text = f"{title or ''} {content or ''}"
    return sorted([word for word in SENSITIVE_WORDS if word in text])


def calculate_heat_score(
    view_count: int = 0,
    like_count: int = 0,
    favorite_count: int = 0,
    comment_count: int = 0,
) -> float:
    return round(view_count * 0.4 + like_count * 2 + favorite_count * 3 + comment_count * 2.5, 2)


def calculate_quality_score(content_obj) -> float:
    title = getattr(content_obj, "title", "") or ""
    content = getattr(content_obj, "content", "") or ""
    summary = getattr(content_obj, "summary", "") or ""
    tags = getattr(content_obj, "tags", "") or ""
    cover_url = getattr(content_obj, "cover_url", "") or ""
    view_count = getattr(content_obj, "view_count", 0) or 0
    like_count = getattr(content_obj, "like_count", 0) or 0
    favorite_count = getattr(content_obj, "favorite_count", 0) or 0
    comment_count = getattr(content_obj, "comment_count", 0) or 0

    score = 0.0
    score += 15 if 8 <= len(title) <= 80 else 8
    score += min(len(content) / 800 * 30, 30)
    score += 15 if len(summary) >= 40 else 6 if summary else 0
    score += 15 if tags else 0
    score += 10 if cover_url else 0
    interaction = math.log1p(view_count + like_count * 3 + favorite_count * 4 + comment_count * 4)
    score += min(interaction * 3, 15)
    return round(min(score, 100), 2)


def analyze_content_payload(title: str, content: str, content_obj=None) -> dict:
    keywords = extract_keywords(title, content)
    summary = generate_summary(content)
    category = classify_content(title, content, keywords)
    sentiment = analyze_sentiment(content)
    sensitive_words = detect_sensitive_words(title, content)

    if content_obj is None:
        class Temp:
            pass

        content_obj = Temp()
        content_obj.title = title
        content_obj.content = content
        content_obj.summary = summary
        content_obj.tags = ",".join(keywords)
        content_obj.cover_url = ""
        content_obj.view_count = 0
        content_obj.like_count = 0
        content_obj.favorite_count = 0
        content_obj.comment_count = 0

    quality_score = calculate_quality_score(content_obj)
    heat_score = calculate_heat_score(
        getattr(content_obj, "view_count", 0) or 0,
        getattr(content_obj, "like_count", 0) or 0,
        getattr(content_obj, "favorite_count", 0) or 0,
        getattr(content_obj, "comment_count", 0) or 0,
    )
    return {
        "keywords": keywords,
        "summary": summary,
        "category": category,
        "sentiment": sentiment,
        "sensitive_words": sensitive_words,
        "quality_score": quality_score,
        "heat_score": heat_score,
        "analyzed_at": datetime.utcnow().isoformat(),
    }
