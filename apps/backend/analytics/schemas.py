# analytics/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TrendingPostResponse(BaseModel):
    post_id: str
    author: Optional[str] = None
    caption: Optional[str] = None
    score: Optional[float] = None
    score_trend: Optional[float] = None
    posted_at: Optional[datetime] = None

class HashtagStatsResponse(BaseModel):
    id: int
    name: str
    platform: str
    total_posts: Optional[int] = None
    avg_engagement: Optional[float] = None
    last_scraped: Optional[datetime] = None
    updated_at: Optional[datetime] = None
