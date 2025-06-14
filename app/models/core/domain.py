from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class Domain(BaseModel):
    domain: str                             # e.g., 'spamsite.com'
    homepage_url: Optional[HttpUrl] = None  # optional landing page
    registrant_name: Optional[str] = None
    registrant_org: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    is_expired: bool = False
    first_seen_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None

    source: Optional[str] = None            # e.g., 'manual', 'CSE'
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "domain": "spamsite.com",
                "homepage_url": "http://spamsite.com",
                "registrant_name": "John Doe",
                "registrant_org": "Spam Networks Ltd",
                "city": "Lagos",
                "country": "NG",
                "is_expired": False,
                "first_seen_at": "2024-06-01T12:00:00Z",
                "last_verified_at": "2024-06-10T14:00:00Z",
                "source": "CSE",
                "notes": "Frequently linked by sink channels"
            }
        }
