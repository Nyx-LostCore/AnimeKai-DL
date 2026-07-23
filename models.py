from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class AnimeMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    slug: Optional[str] = None
    ani_id: Optional[str] = None

    season: Optional[int] = None
    episodes: Optional[int] = None

    default_quality: Optional[str] = None
    source: Optional[str] = None

    # ongoing / completed / hiatus
    status: Optional[str] = Field(default="unknown")

    created_at: datetime = Field(default_factory=datetime.utcnow)