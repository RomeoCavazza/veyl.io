# projects/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    platforms: List[str] = Field(default_factory=list)
    scope_type: Optional[str] = None  # 'hashtags', 'creators', 'both'
    scope_query: Optional[str] = None
    # Pour la création: listes des hashtags/users à ajouter
    hashtag_names: Optional[List[str]] = Field(default_factory=list)  # ["fashion", "style"]
    creator_usernames: Optional[List[str]] = Field(default_factory=list)  # ["@user1", "@user2"]

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    platforms: Optional[List[str]] = None
    scope_type: Optional[str] = None
    scope_query: Optional[str] = None
    hashtag_names: Optional[List[str]] = None
    creator_usernames: Optional[List[str]] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: UUID
    name: str
    description: Optional[str] = None
    status: str
    platforms: List[str] = Field(default_factory=list)
    scope_type: Optional[str] = None
    scope_query: Optional[str] = None
    creators_count: int = 0
    posts_count: int = 0
    signals_count: int = 0
    last_run_at: Optional[datetime] = None
    last_signal_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # Données liées (optionnel, pour affichage)
    hashtags: Optional[List[dict]] = None  # Liste des hashtags liés
    creators: Optional[List[dict]] = None  # Liste des créateurs liés
    
    class Config:
        from_attributes = True


class ProjectPostResponse(BaseModel):
    id: str
    author: Optional[str] = None
    username: Optional[str] = None  # Alias pour author (compatibilité frontend)
    caption: Optional[str] = None
    media_url: Optional[str] = None
    permalink: Optional[str] = None
    posted_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    platform: Optional[str] = None
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    share_count: Optional[int] = 0
    view_count: Optional[int] = 0
    score_trend: Optional[float] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    location: Optional[str] = None
    media_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    external_id: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectCreatorCreate(BaseModel):
    username: str
    platform: str = Field(default="instagram", min_length=1)


class ProjectHashtagCreate(BaseModel):
    hashtag: str = Field(..., min_length=1)
    platform: str = Field(default="instagram", min_length=1)

    class Config:
        populate_by_name = True

