from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChannelVideoComment(BaseModel):
    comment_id: str                      # YouTube comment ID (document ID or field)
    channel_id: str                      # Who posted the comment (feeder)
    video_id: str                        # Which video was commented on
    text: str                            # Full comment text
    like_count: Optional[int] = None
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    source: Optional[str] = None         # 'API', 'manual', etc.
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "comment_id": "Ugxyz123abc456",
                "channel_id": "UC987feedbot",
                "video_id": "dQw4w9WgXcQ",
                "text": "This method really works! 😲 Check it out.",
                "like_count": 12,
                "published_at": "2024-06-12T13:45:00Z",
                "updated_at": "2024-06-12T14:00:00Z",
                "source": "API",
                "notes": "Flagged as typical engagement bait"
            }
        }