import os
import logging
from typing import Optional, List
from playwright.async_api import async_playwright
from app.utils.pattern import extract_domain_from_text

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Selectors
DEFAULT_HANDLE_SELECTOR = "div.yt-content-metadata-view-model-wiz__metadata-row span.yt-core-attributed-string--link-inherit-color"
DEFAULT_LINK_SELECTOR = "yt-attribution-view-model a.yt-core-attributed-string__link"
FEATURED_CHANNEL_SELECTOR = "div#channel > a#channel-info"
HANDLE_ELEMENT = os.environ.get("HANDLE_ELEMENT", DEFAULT_HANDLE_SELECTOR)


# ✅ Helper
def channel_ref_to_url(ref: str) -> str:
    if ref.startswith("UC"):
        return f"https://www.youtube.com/channel/{ref}"
    elif ref.startswith("@"):
        return f"https://www.youtube.com/{ref}"
    else:
        return f"https://www.youtube.com/@{ref}"


# ✅ 1. Get channel handle (async version)
async def get_channel_handle(channel_url: str) -> str:
    logger.info(f"Launching browser to get handle from: {channel_url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            logger.info(f"Navigating to {channel_url}")
            await page.goto(channel_url, wait_until="domcontentloaded", timeout=30000)

            logger.info(f"Looking for handle using selector: {HANDLE_ELEMENT}")
            handle_elem = await page.query_selector(HANDLE_ELEMENT)

            if handle_elem:
                handle = await handle_elem.inner_text()
                logger.info(f"Extracted handle: {handle}")
            else:
                handle = "N/A"
                logger.warning("Handle element not found.")
            
            await browser.close()
            return handle
    except Exception as e:
        logger.error(f"Error extracting handle: {e}")
        return "N/A"


# ✅ 2. Get channel domain
async def get_channel_external_url(channel_identifier: str) -> Optional[str]:
    logger.info(f"Launching browser to get domain from: {channel_identifier}")
    channel_url = channel_ref_to_url(channel_identifier)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(channel_url, wait_until="domcontentloaded", timeout=30000)
            external_url_elem = await page.query_selector(DEFAULT_LINK_SELECTOR)

            if external_url_elem:
                external_url = await external_url_elem.inner_text()
                logger.info(f"Extracted domain: {external_url}")
            else:
                external_url = None
                logger.warning("Domain element not found.")

            await browser.close()
            return external_url
    except Exception as e:
        logger.error(f"Error extracting domain from {channel_url}: {e}")
        return None


# ✅ 3. Get featured channel links
async def get_featured_channel_links(channel_identifier: str) -> List[str]:
    logger.info(f"Launching browser to extract featured channel links from: {channel_identifier}")
    channel_url = channel_ref_to_url(channel_identifier)
    links = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(channel_url, wait_until="networkidle", timeout=60000)
            anchor_elements = await page.query_selector_all(FEATURED_CHANNEL_SELECTOR)

            for anchor in anchor_elements:
                href = await anchor.get_attribute('href')
                if href:
                    cleaned = href.lstrip('/')
                    links.append(cleaned)
                    logger.debug(f"Found featured link: {cleaned}")

            await browser.close()
            return links
    except Exception as e:
        logger.error(f"Error extracting featured links from {channel_url}: {e}")
        return []
