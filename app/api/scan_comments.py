from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

from app.services.comment_scanner import scan_video_for_channel_comment
from app.utils.pattern import extract_video_id, extract_channel_id
from app.services.firestore_client import get_all_bot_channel_ids, create_channel, create_channel_channel_link, create_domain_from_text  # Optional fallback behavior
from app.services.youtube_client import fetch_top_comments  #TODO
from app.utils.pattern import is_suspicious_name #TODO
from app.services.vision import is_profile_image_flagged #TODO
from app.services.youtube_client import get_featured_channels, get_channel_description #TODO

router = APIRouter()

class ScanCommentsRequest(BaseModel):
    video_url: HttpUrl
    channel_urls: Optional[List[HttpUrl]] = None  # If not provided, scan all known bot channels

class DetectBotsRequest(BaseModel):
    video_url: HttpUrl
    like_threshold: Optional[int] = 10

@router.post("/scan_known_bots")
async def scan_known_bots(request: ScanCommentsRequest):
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


@router.post("/detect_bots")
async def detect_bots(request: DetectBotsRequest):
    try:
        video_id = extract_video_id(str(request.video_url))
        comments = await fetch_top_comments(video_id, limit=1000)

        flagged = []

        for comment in comments:
            if comment.get("likeCount", 0) < request.like_threshold:
                continue

            author_name = comment.get("authorDisplayName", "")
            author_channel_id = comment.get("authorChannelId", {}).get("value")
            author_profile_img = comment.get("authorProfileImageUrl", "")

            if not is_suspicious_name(author_name):
                continue

            if not await is_profile_image_flagged(author_profile_img):
                continue

            # Flagged bot logic
            await create_channel(author_channel_id, {
                "profile_url": author_profile_img,
                "source": "automated_flag",
                "notes": f"Flagged via comment on {video_id}"
            })

            # Crawl featured channels
            featured = await get_featured_channels(author_channel_id)
            for f_id in featured:
                await create_channel_link(author_channel_id, f_id) #TODO

            # Check description for domains
            description = await get_channel_description(author_channel_id)
            await create_domain_from_text(description, discovered_by=author_channel_id) #TODO

            flagged.append(author_channel_id)

        return {
            "status": "success",
            "video_id": video_id,
            "flagged_channels": flagged,
            "count": len(flagged)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot detection failed: {e}")