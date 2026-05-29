from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.behavior import UserBehavior
from app.models.content import Content
from app.models.recommendation_log import RecommendationLog
from app.models.user import User
from app.services.content_service import content_to_dict, split_tags


def dashboard_summary(db: Session) -> dict:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    content_count = db.query(Content).count()
    user_count = db.query(User).count()
    behavior_count = db.query(UserBehavior).count()
    today_views = (
        db.query(UserBehavior)
        .filter(UserBehavior.action_type == "view", UserBehavior.created_at >= today_start)
        .count()
    )
    today_recommend_clicks = (
        db.query(RecommendationLog)
        .filter(RecommendationLog.action == "click", RecommendationLog.created_at >= today_start)
        .count()
    )

    category_rows = db.query(Content.category, func.count(Content.id)).group_by(Content.category).all()
    category_distribution = [{"name": name or "未分类", "value": count} for name, count in category_rows]

    hot_contents = db.query(Content).order_by(Content.heat_score.desc()).limit(10).all()

    trend = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = db.query(UserBehavior).filter(UserBehavior.created_at >= day, UserBehavior.created_at < next_day).count()
        trend.append({"date": day.strftime("%m-%d"), "value": count})

    tag_counter = Counter()
    for user in db.query(User).all():
        tag_counter.update(split_tags(user.interests))
    interest_distribution = [{"name": tag, "value": count} for tag, count in tag_counter.most_common(10)]

    return {
        "content_count": content_count,
        "user_count": user_count,
        "behavior_count": behavior_count,
        "today_views": today_views,
        "today_recommend_clicks": today_recommend_clicks,
        "category_distribution": category_distribution,
        "hot_contents": [content_to_dict(item) for item in hot_contents],
        "behavior_trend": trend,
        "interest_distribution": interest_distribution,
    }
