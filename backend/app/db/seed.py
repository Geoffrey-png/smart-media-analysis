"""演示数据播种服务。

提供两种模式：
- seed_demo_data(db)：向已有会话写入演示数据（不删表）
- seed_if_empty(db)：仅当用户表为空时才播种，返回是否执行
"""

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.algorithms.content_analyzer import calculate_heat_score, calculate_quality_score
from app.models.category import Category
from app.models.content import Content
from app.models.tag import Tag
from app.models.user import User
from app.services.security_service import hash_password

CATEGORIES = [
    ("科技", "人工智能、互联网、软件、硬件和数字化"),
    ("财经", "宏观经济、企业、资本市场和投资"),
    ("体育", "赛事、球队、运动员和体育产业"),
    ("娱乐", "电影、音乐、综艺和明星动态"),
    ("社会", "民生、教育、交通、公共服务"),
    ("文化", "文旅、艺术、阅读和非遗"),
    ("国际", "全球资讯、海外市场和国际关系"),
    ("健康", "医疗、心理、运动和生活方式"),
]

TAG_POOL = [
    "人工智能", "大模型", "数据治理", "机器人", "芯片",
    "金融", "投资", "消费", "市场", "企业",
    "足球", "篮球", "冠军", "联赛", "训练",
    "电影", "音乐", "综艺", "票房", "明星",
    "教育", "医疗", "交通", "城市", "就业",
    "旅游", "非遗", "展览", "国际", "健康",
]

USERS = [
    ("tech_user", "科技观察者", 25, "male", "杭州", ["人工智能", "大模型", "芯片"]),
    ("finance_user", "财经读者", 32, "female", "上海", ["金融", "投资", "市场"]),
    ("sports_user", "运动爱好者", 22, "male", "广州", ["足球", "篮球", "冠军"]),
    ("ent_user", "娱乐达人", 28, "female", "北京", ["电影", "音乐", "综艺"]),
    ("life_user", "民生关注者", 36, "unknown", "成都", ["教育", "医疗", "交通"]),
]

CATEGORY_TAGS = {
    "科技": ["人工智能", "大模型", "芯片", "数据治理", "机器人"],
    "财经": ["金融", "投资", "市场", "消费", "企业"],
    "体育": ["足球", "篮球", "冠军", "联赛", "训练"],
    "娱乐": ["电影", "音乐", "综艺", "票房", "明星"],
    "社会": ["教育", "医疗", "交通", "城市", "就业"],
    "文化": ["旅游", "非遗", "展览", "城市", "消费"],
    "国际": ["国际", "市场", "企业", "金融", "交通"],
    "健康": ["健康", "医疗", "运动", "心理", "城市"],
}


def _make_content(index: int, category: str, tags: list[str]) -> Content:
    title = f"{category}观察：{tags[0]}领域出现新变化 {index}"
    body = (
        f"近日，{category}领域围绕{tags[0]}、{tags[1]}和{tags[2]}展开了新的实践。"
        f"多家机构表示，相关创新正在提升行业效率，也带来新的市场机会。"
        f"业内人士认为，未来一段时间，{tags[0]}将继续影响用户体验、内容生产和商业模式。"
        f"本报道结合数据、案例和专家观点，对事件背景、发展趋势和潜在风险进行了梳理。"
    )
    view = random.randint(50, 3000)
    like = random.randint(1, 300)
    fav = random.randint(0, 120)
    comment = random.randint(0, 100)
    content = Content(
        title=title,
        summary=body[:120],
        content=body,
        author=random.choice(["系统编辑", "融媒记者", "数据新闻实验室", "城市观察"]),
        category=category,
        tags=",".join(tags),
        cover_url=f"https://picsum.photos/seed/media-{index}/640/360",
        content_type=random.choice(["article", "article", "video", "image"]),
        publish_time=datetime.utcnow() - timedelta(days=random.randint(0, 45)),
        view_count=view,
        like_count=like,
        favorite_count=fav,
        comment_count=comment,
    )
    content.heat_score = calculate_heat_score(view, like, fav, comment)
    content.quality_score = calculate_quality_score(content)
    content.sentiment = random.choice(["positive", "neutral", "neutral", "negative"])
    content.status = random.choice(["published", "published", "published", "pending"])
    return content


def seed_demo_data(db: Session) -> None:
    """向已有会话写入完整演示数据（不建表、不删表）。

    调用方负责 commit。"""
    db.add_all([Category(name=name, description=desc) for name, desc in CATEGORIES])
    db.add_all([Tag(name=name, count=random.randint(1, 20)) for name in TAG_POOL])

    users = [
        User(
            username=username,
            nickname=nickname,
            age=age,
            gender=gender,
            city=city,
            interests=",".join(interests),
            password_hash=hash_password("demo"),
        )
        for username, nickname, age, gender, city, interests in USERS
    ]
    db.add_all(users)
    db.flush()

    contents = []
    for i in range(30):
        category = CATEGORIES[i % len(CATEGORIES)][0]
        tags = random.sample(CATEGORY_TAGS[category], 3)
        contents.append(_make_content(i + 1, category, tags))
    db.add_all(contents)
    db.flush()

    actions = ["view", "view", "view", "like", "favorite", "comment", "share", "dislike"]
    for _ in range(120):
        user = random.choice(users)
        content = random.choice(contents)
        action = random.choice(actions)
        from app.models.behavior import UserBehavior

        db.add(
            UserBehavior(
                user_id=user.id,
                content_id=content.id,
                action_type=action,
                duration=random.randint(5, 360),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23)),
            )
        )

    # 写回用户默认角色（tech_user=admin 等）
    db.flush()
    db.execute(db.query(User).filter(User.username == "tech_user").update({"role": "admin"}, synchronize_session=False))
    db.execute(db.query(User).filter(User.username == "finance_user").update({"role": "editor"}, synchronize_session=False))
    db.execute(db.query(User).filter(User.username == "ent_user").update({"role": "auditor"}, synchronize_session=False))

    print("演示数据播种完成：30 条内容、5 个用户、120 条行为。")


def seed_if_empty(db: Session) -> bool:
    """仅当用户表为空时播种。返回 True 表示执行了播种。"""
    if db.query(User).count() > 0:
        return False
    seed_demo_data(db)
    db.commit()
    return True
