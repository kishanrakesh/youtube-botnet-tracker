from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from app.services.comment_scanner import scan_video_for_channel_comment
from app.utils.extract import extract_video_id, extract_channel_id
from app.services.firestore_client import get_all_bot_channel_ids  # Optional fallback behavior

router = APIRouter()

class ScanCommentsRequest(BaseModel):
    video_url: HttpUrl
    channel_urls: Optional[List[HttpUrl]] = None  # If not provided, scan all known bot channels

@router.post("/")
async def scan_comments(request: ScanCommentsRequest):
    try:
        video_id = extract_video_id(str(request.video_url))

        if request.channel_urls:
            channel_ids = [extract_channel_id(str(url)) for url in request.channel_urls]
        else:
            channel_ids = await get_all_bot_channel_ids()

        if not channel_ids:
            raise HTTPException(status_code=400, detail="No bot channels provided or found in the system.")

        matched_comments = await scan_video_for_channel_comment(video_id, channel_ids)

        return {
            "status": "success",
            "video_id": video_id,
            "matched_count": len(matched_comments),
            "matched_comments": matched_comments,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan comments: {e}")
