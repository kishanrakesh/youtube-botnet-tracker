from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class Channel(BaseModel):
    channel_id: str                          # YouTube channel ID (document ID)
    name: Optional[str] = None               # Channel name/title
    handle: Optional[str] = None             # e.g., @channelname
    description: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None

    featured_channel_ids: List[str] = Field(default_factory=list)
    linked_domains: List[str] = Field(default_factory=list)

    is_sink: bool = False
    is_feeder: bool = False
    inactive: bool = False
    source: Optional[str] = None             # e.g., 'CSE', 'manual'
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "channel_id": "UCabc123xyz",
                "name": "SpamTube",
                "handle": "@spamtube",
                "description": "Crypto tricks & giveaways!",
                "thumbnail_url": "https://yt3.ggpht.com/ytc/abc123/photo.jpg",
                "featured_channel_ids": ["UCxyz456def"],
                "linked_domains": ["spamsite.com"],
                "is_sink": True,
                "is_feeder": False,
                "inactive": False,
                "source": "CSE",
                "notes": "First seen linked to domain xyz.com",
                "created_at": "2024-06-13T10:00:00Z"
            }
        }