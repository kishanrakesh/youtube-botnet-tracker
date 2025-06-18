import httpx
from typing import Dict, List, Optional

from app.utils.env import get_api_key
from app.utils.logging import get_logger
from app.config import YOUTUBE_API_BASE, YOUTUBE_COMMENTS_PAGE_LIMIT

logger = get_logger(__name__)
API_KEY = get_api_key()


async def fetch_channel_metadata_by_id(channel_id: str) -> Optional[Dict]:
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


async def fetch_channel_metadata_by_handle(handle: str) -> Optional[Dict]:
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {
        "part": "snippet,statistics",
        "forHandle": handle,
        "key": API_KEY
    }

    

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if "items" in data and data["items"]:
            return data["items"][0]
        logger.warning(f"No metadata found for channel {handle}")
        return None

async def fetch_video_metadata(video_id: str) -> Optional[Dict]:
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "snippet,statistics,topicDetails",
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
        "part": "snippet,replies",
        "videoId": video_id,
        "key": API_KEY,
        "maxResults": 100,
        "order": "relevance",
        "textFormat": "plainText"
    }

    async with httpx.AsyncClient() as client:
        for _ in range(YOUTUBE_COMMENTS_PAGE_LIMIT):
            resp = await client.get(url, params=params)
            data = resp.json()
            if "items" in data:
                for item in data["items"]:
                    comment = item["snippet"]["topLevelComment"]
                    comment["totalReplyCount"] = item["snippet"]["totalReplyCount"]
                    if not author_channel_ids or comment["snippet"]["authorChannelId"]["value"] in author_channel_ids:
                        results.append(comment)
                        
                    if "replies" in item:
                        for replies in item["replies"]["comments"]:

                            replies["totalReplyCount"] = 0
                            print(replies)
                            results.append(replies)

            if "nextPageToken" in data:
                params["pageToken"] = data["nextPageToken"]
            else:
                break

    logger.info(f"Fetched {len(results)} comments for video {video_id}")
    return results


async def fetch_top_comments(video_id: str) -> List[Dict]:
    """
    Fetches up to 1000 top-level comments for a YouTube video, ordered by relevance.
    """
    url = f"{YOUTUBE_API_BASE}/commentThreads"
    comments = []
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": 100,
        "order": "relevance",
        "textFormat": "plainText",
        "key": API_KEY
    }

    async with httpx.AsyncClient() as client:
        for _ in range(50):
            logger.info(f"Fetching comment page for video {video_id}...")
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append(comment)

            if "nextPageToken" in data and len(comments):
                params["pageToken"] = data["nextPageToken"]
            else:
                break

    logger.info(f"Fetched {len(comments)} comments from video {video_id}")
    return comments


async def get_featured_channels(video_id: str) -> List[Dict]:
    #TODO
    pass

async def get_channel_description(video_id: str) -> List[Dict]:
    #TODO
    pass