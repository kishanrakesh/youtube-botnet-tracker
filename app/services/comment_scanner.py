from typing import List, Optional
from app.services.youtube import fetch_comments
from app.services.firestore_client import store_comment
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def scan_video_for_channel_comment(video_id: str, channel_ids: str) -> Optional[dict]:
    """
    Searches for a comment by a specific channel on a specific video.
    If found, stores it in Firestore and returns the comment.
    """
    logger.info(f"Scanning video {video_id} for comment by channel {channel_ids}")
    comments = await fetch_comments(video_id, author_channel_ids=channel_ids)
    if comments:
        for comment in comments:
            await store_comment(video_id, channel_ids, comment)
            logger.info(f"Stored comment by channel {channel_ids} on video {video_id}")
        return comments  # return the first match
    else:
        logger.info(f"No comments by channel {channel_ids} on video {video_id}")
        return []


async def scan_video_for_all_known_bots(video_id: str, bot_channel_ids: List[str]) -> List[dict]:
    """
    Scans a video for comments from all known bot channels.
    Stores any matches and returns the list of matched comments.
    """
    logger.info(f"Scanning video {video_id} for known bot comments...")
    matched_comments = []

    for channel_id in bot_channel_ids:
        comments = await fetch_comments(video_id, author_channel_ids=channel_id)
        for comment in comments:
            await store_comment(video_id, channel_id, comment)
            matched_comments.append(comment)

    logger.info(f"Found {len(matched_comments)} comments from known bots on video {video_id}")
    return matched_comments