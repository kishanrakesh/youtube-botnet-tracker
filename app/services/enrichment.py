from datetime import datetime
from typing import Optional

from app.services.youtube_client import fetch_channel_metadata_by_id
from app.services.firestore_client import update_channel_by_id, get_channel_by_id
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def enrich_channel(channel_id: str) -> bool:
    """
    Fetches metadata from YouTube API and updates the corresponding Firestore document.
    Returns True if successful.
    """
    metadata = await fetch_channel_metadata_by_id(channel_id)
    if not metadata:
        logger.warning(f"Failed to enrich channel {channel_id}")
        return False

    snippet = metadata.get("snippet", {})
    stats = metadata.get("statistics", {})

    update_data = {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "published_at": snippet.get("publishedAt"),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "country": snippet.get("country"),
        "enriched_at": datetime.utcnow().isoformat()
    }

    await update_channel_by_id(channel_id, update_data)
    logger.info(f"Channel {channel_id} enriched.")
    return True


async def enrich_domain(domain: str) -> Optional[dict]:
    """
    Placeholder for domain WHOIS lookup and enrichment.
    Replace this with actual WHOIS API call or scraping logic.
    """
    logger.info(f"Enriching domain {domain} – feature not implemented yet.")
    return None
