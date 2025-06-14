# app/routes/add_channel.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from app.services.firestore_client import add_channel_with_links
from app.utils.extract import extract_video_id, extract_channel_id

router = APIRouter()

class AddChannelRequest(BaseModel):
    channel_url: HttpUrl
    video_url: Optional[HttpUrl] = None
    featured_channels: Optional[List[HttpUrl]] = []
    linked_domain: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

@router.post("/")
async def add_channel(request: AddChannelRequest):
    try:
        channel_id = extract_channel_id(str(request.channel_url))
        video_id = extract_video_id(str(request.video_url)) if request.video_url else None
        featured_ids = [extract_channel_id(str(url)) for url in request.featured_channels] if request.featured_channels else []

        result = await add_channel_with_links(
            channel_id=channel_id,
            video_id=video_id,
            featured_channel_ids=featured_ids,
            linked_domain=request.linked_domain,
            source=request.source,
            notes=request.notes,
        )

        return {"status": "success", "channel": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add channel: {e}")
