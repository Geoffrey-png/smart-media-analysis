from pydantic import BaseModel


class BehaviorCreate(BaseModel):
    user_id: int
    content_id: int
    action_type: str
    duration: int = 0

