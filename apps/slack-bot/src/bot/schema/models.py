from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    RSS = "rss"
    API = "api"
    WEBSITE = "website"
    PDF = "pdf"



class Article(BaseModel):
    title: str
    url: HttpUrl
    source: str
    source_type: SourceType
    content: str
    published_date: datetime
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Brief(BaseModel):
    title: str
    problem_statement: str
    objectives: List[str]
    kpis: List[str]
    budget: Optional[str]
    deadline: Optional[datetime]
    context: str
    constraints: List[str]
    attachments: List[str] = Field(default_factory=list)

class SlideTemplate(BaseModel):
    name: str
    layout: Dict[str, Any]
    theme: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Report(BaseModel):
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    slides: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    template: Optional[SlideTemplate] = None 