import httpx
from typing import Dict, List, Optional

from app.utils.env import get_api_key
from app.utils.logging import get_logger
from app.config import YOUTUBE_API_BASE, YOUTUBE_COMMENTS_PAGE_LIMIT

logger = get_logger(__name__)
API_KEY = get_api_key()


async def fetch_channel_metadata(channel_id: str) -> Optional[Dict]:
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }

    

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if "items" in data and data["items"]:
            return data["items"][0]
        logger.warning(f"No metadata found for channel {channel_id}")
        return None
            


async def fetch_video_metadata(video_id: str) -> Optional[Dict]:
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": API_KEY
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if "items" in data and data["items"]:
            return data["items"][0]
        logger.warning(f"No metadata found for video {video_id}")
        return None


async def fetch_comments(video_id: str, author_channel_ids: Optional[List[str]] = None) -> List[Dict]:
    """
    Returns a list of comment threads. If author_channel_ids is provided, filters for that author.
    """
    url = f"{YOUTUBE_API_BASE}/commentThreads"
    results = []
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": API_KEY,
        "maxResults": 100,
        "textFormat": "plainText"
    }

    async with httpx.AsyncClient() as client:
        for _ in range(YOUTUBE_COMMENTS_PAGE_LIMIT):
            resp = await client.get(url, params=params)
            data = resp.json()
            if "items" in data:
                for item in data["items"]:
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    comment["id"] = item["snippet"]["topLevelComment"]["id"]
                    print(comment.get("authorChannelId", {}).get("value"))
                    print(author_channel_ids)
                    print(comment.get("authorChannelId", {}).get("value") in author_channel_ids)
                    print()
                    if not author_channel_ids or comment.get("authorChannelId", {}).get("value") in author_channel_ids:
                        results.append(comment)

            if "nextPageToken" in data:
                params["pageToken"] = data["nextPageToken"]
            else:
                break

    logger.info(f"Fetched {len(results)} comments for video {video_id}")
    return results