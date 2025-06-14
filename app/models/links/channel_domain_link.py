from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class ChannelDomainLink(BaseModel):
    channel_id: str                       # The YouTube channel linking out
    domain: str                           # The domain being linked to (e.g. spamsite.com)
    full_url: Optional[HttpUrl] = None    # Full URL (if known), e.g. http://spamsite.com/landing
    discovered_at: Optional[datetime] = None
    source: Optional[str] = None          # e.g., "CSE", "manual"
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "channel_id": "UCxyz789sink",
                "domain": "spamsite.com",
                "full_url": "https://spamsite.com/signup",
                "discovered_at": "2024-06-11T15:20:00Z",
                "source": "CSE",
                "notes": "Link found in YouTube About section"
            }
        }