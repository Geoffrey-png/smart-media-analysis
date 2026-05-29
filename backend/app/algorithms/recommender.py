from collections import defaultdict
from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.algorithms.content_analyzer import extract_keywords
from app.models.behavior import UserBehavior
from app.models.content import Content
from app.services.content_service import content_to_dict, split_tags
from app.services.user_service import ACTION_WEIGHTS, build_user_profile


def normalize(value: float, max_value: float = 100.0) -> float:
    if max_value <= 0:
        return 0
    return min(max(value / max_value, 0), 1)


def freshness_score(publish_time) -> float:
    if not publish_time:
        return 0.3
    days = max((datetime.utcnow() - publish_time).days, 0)
    if days <= 1:
        return 1
    if days <= 7:
        return 0.82
    if days <= 30:
        return 0.55
    return 0.22


def tag_match_score(user_tags: dict[str, float], content_tags: list[str], category: str | None = None) -> float:
    if not user_tags:
        return 0
    positive_sum = sum(max(v, 0) for v in user_tags.values()) or 1
    matched = sum(max(user_tags.get(tag, 0), 0) for tag in content_tags)
    if category:
        matched += max(user_tags.get(category, 0), 0) * 0.7
    return min(matched / positive_sum, 1)


def build_tag_weights_from_behaviors(db: Session, user_id: int) -> tuple[dict[str, float], set[int], set[str]]:
    tag_weights: defaultdict[str, float] = defaultdict(float)
    viewed_content_ids: set[int] = set()
    negative_tags: set[str] = set()
    rows = (
        db.query(UserBehavior, Content)
        .join(Content, UserBehavior.content_id == Content.id)
        .filter(UserBehavior.user_id == user_id)
        .all()
    )
    for behavior, content in rows:
        if behavior.action_type in {"view", "like", "favorite", "comment", "share", "dislike"}:
            viewed_content_ids.add(content.id)
        weight = ACTION_WEIGHTS.get(behavior.action_type, 0)
        if behavior.action_type == "view":
            weight += min((behavior.duration or 0) / 120, 2)
        for tag in split_tags(content.tags):
            tag_weights[tag] += weight
            if behavior.action_type == "dislike":
                negative_tags.add(tag)
        if content.category:
            tag_weights[content.category] += weight * 0.6
    return dict(tag_weights), viewed_content_ids, negative_tags


def recommend_hot(db: Session, limit: int = 10, exclude_ids: set[int] | None = None) -> list[dict]:
    exclude_ids = exclude_ids or set()
    query = db.query(Content).filter(Content.status == "published")
    if exclude_ids:
        query = query.filter(~Content.id.in_(exclude_ids))
    contents = query.order_by(desc(Content.heat_score), desc(Content.view_count), desc(Content.publish_time)).limit(limit).all()
    results = []
    for content in contents:
        item = content_to_dict(content)
        item["recommend_score"] = round(normalize(content.heat_score or 0, 500) * 100, 2)
        item["reason"] = "近期热度较高"
        results.append(item)
    return results


def recommend_for_user(db: Session, user_id: int, limit: int = 10) -> list[dict]:
    profile = build_user_profile(db, user_id)
    user_tags = {item["tag"]: item["weight"] for item in profile.get("interest_tags", [])}
    behavior_tags, viewed_ids, negative_tags = build_tag_weights_from_behaviors(db, user_id)
    for key, value in behavior_tags.items():
        user_tags[key] = user_tags.get(key, 0) + value

    max_heat = db.query(Content).filter(Content.status == "published").order_by(desc(Content.heat_score)).first()
    max_heat_value = max_heat.heat_score if max_heat else 100
    candidates = (
        db.query(Content)
        .filter(Content.status == "published")
        .order_by(desc(Content.publish_time), desc(Content.id))
        .limit(500)
        .all()
    )

    scored = []
    for content in candidates:
        if content.id in viewed_ids:
            continue
        tags = split_tags(content.tags)
        penalty = 0.45 if any(tag in negative_tags for tag in tags) else 1
        t_score = tag_match_score(user_tags, tags, content.category)
        h_score = normalize(content.heat_score or 0, max_heat_value or 100)
        q_score = normalize(content.quality_score or 0, 100)
        f_score = freshness_score(content.publish_time)
        score = (t_score * 0.52 + h_score * 0.18 + q_score * 0.18 + f_score * 0.12) * penalty

        matched = [tag for tag in tags if user_tags.get(tag, 0) > 0]
        if content.category and user_tags.get(content.category, 0) > 0:
            matched.insert(0, content.category)
        if matched:
            reason = f"因为你最近关注「{matched[0]}」"
        elif h_score > 0.6:
            reason = "近期热度较高"
        elif q_score > 0.7:
            reason = "内容质量评分较高"
        else:
            reason = "为你探索新的内容方向"
        item = content_to_dict(content)
        item["recommend_score"] = round(score * 100, 2)
        item["reason"] = reason
        scored.append(item)

    scored.sort(key=lambda x: x["recommend_score"], reverse=True)
    selected = diversify(scored, limit)
    if len(selected) < limit:
        seen = {item["id"] for item in selected} | viewed_ids
        selected += [item for item in recommend_hot(db, limit=limit, exclude_ids=seen) if item["id"] not in seen]
    return selected[:limit]


def diversify(items: list[dict], limit: int = 10) -> list[dict]:
    """控制同一分类占比，避免推荐单一化。"""

    if limit <= 0:
        return []
    category_limit = max(2, limit // 3)
    selected = []
    category_count: defaultdict[str, int] = defaultdict(int)
    for item in items:
        category = item.get("category") or "未知"
        if category_count[category] < category_limit:
            selected.append(item)
            category_count[category] += 1
        if len(selected) >= limit:
            return selected

    selected_ids = {item["id"] for item in selected}
    for item in items:
        if item["id"] not in selected_ids:
            selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def recommend_similar_content(db: Session, content_id: int, limit: int = 10) -> list[dict]:
    target = db.query(Content).filter(Content.id == content_id).first()
    if not target:
        return []
    target_tags = set(split_tags(target.tags))
    target_words = set(extract_keywords(target.title, target.content, top_k=8)) | target_tags
    scored = []
    for content in db.query(Content).filter(Content.id != content_id, Content.status == "published").all():
        tags = set(split_tags(content.tags))
        category_score = 0.3 if content.category == target.category else 0
        tag_score = len(target_tags & tags) / max(len(target_tags | tags), 1)
        text_words = set(extract_keywords(content.title, content.content, top_k=8)) | tags
        text_score = len(target_words & text_words) / max(len(target_words), 1)
        score = tag_score * 0.6 + category_score + text_score * 0.1
        if score > 0:
            item = content_to_dict(content)
            item["recommend_score"] = round(score * 100, 2)
            item["reason"] = "与你浏览过的内容相似"
            scored.append(item)
    scored.sort(key=lambda x: x["recommend_score"], reverse=True)
    return scored[:limit]


def recommend_mixed(db: Session, user_id: int | None = None, limit: int = 10) -> list[dict]:
    if user_id:
        personalized = recommend_for_user(db, user_id, limit=limit)
        if len(personalized) >= limit:
            return personalized[:limit]
        _, viewed_ids, _ = build_tag_weights_from_behaviors(db, user_id)
        seen = {item["id"] for item in personalized} | viewed_ids
        hot = recommend_hot(db, limit=limit, exclude_ids=seen)
        return (personalized + [item for item in hot if item["id"] not in seen])[:limit]
    return recommend_hot(db, limit)
