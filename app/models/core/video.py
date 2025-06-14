from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class Video(BaseModel):
    video_id: str                             # YouTube video ID (document ID)
    title: Optional[str] = None
    description: Optional[str] = None
    channel_id: Optional[str] = None          # Who uploaded it
    channel_name: Optional[str] = None

    published_at: Optional[datetime] = None
    comment_count: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    tags: Optional[list[str]] = None

    scanned_at: Optional[datetime] = None     # Last time we scanned comments

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Never Gonna Give You Up",
                "description": "Official music video by Rick Astley",
                "channel_id": "UC38IQsAvIsxxjztdMZQtwHA",
                "channel_name": "Rick Astley",
                "published_at": "2009-10-25T07:57:00Z",
                "comment_count": 542319,
                "view_count": 1000000000,
                "like_count": 5000000,
                "tags": ["music", "pop", "rickroll"],
                "scanned_at": "2024-06-13T18:00:00Z"
            }
        }