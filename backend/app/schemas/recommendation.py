from pydantic import BaseModel


class RecommendationClick(BaseModel):
    content_id: int
    user_id: int | None = None
    scene: str = "mixed"
    recommend_score: float = 0
    reason: str = ""

