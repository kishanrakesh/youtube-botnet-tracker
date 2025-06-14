from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChannelLink(BaseModel):
    source_channel_id: str                  # The channel doing the featuring
    target_channel_id: str                  # The channel being featured
    discovered_at: Optional[datetime] = None
    source: Optional[str] = None            # e.g., "CSE", "manual"
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "source_channel_id": "UCabc123feeder",
                "target_channel_id": "UCxyz789sink",
                "discovered_at": "2024-06-12T18:30:00Z",
                "source": "CSE",
                "notes": "Seen via featured section on YouTube"
            }
        }