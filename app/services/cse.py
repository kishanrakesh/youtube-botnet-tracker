import httpx
from typing import List, Dict

from app.utils.env import get_api_key, get_cse_engine_id
from app.utils.logging import get_logger
from app.config import CSE_API_BASE, CSE_RESULTS_PER_DOMAIN

logger = get_logger(__name__)
API_KEY = get_api_key()
ENGINE_ID = get_cse_engine_id()


async def discover_sink_channels_for_domains(domain: str) -> List[Dict]:
    """Searches YouTube channels that mention a given domain."""
    query = f'"{domain}"'
    return await _perform_search(query)


async def search_channels_featuring_channel(channel_url: str) -> List[Dict]:
    """Searches for channels that feature the given channel (sink/referrer logic)."""
    query = f'"{channel_url}"'
    return await _perform_search(query)


async def _perform_search(query: str) -> List[Dict]:
    """Helper to call Google Custom Search API."""
    params = {
        "key": API_KEY,
        "cx": ENGINE_ID,
        "exactTerms": query,
        "q": query,
        "num": CSE_RESULTS_PER_DOMAIN
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(CSE_API_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
    except httpx.HTTPError as e:
        logger.error(f"CSE query failed: {query} | Error: {e}")
        return []