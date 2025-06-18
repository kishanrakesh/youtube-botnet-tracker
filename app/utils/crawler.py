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


def channel_ref_to_url(ref: str) -> str:
    if ref.startswith("UC"):
        return f"https://www.youtube.com/channel/{ref}"
    elif ref.startswith("@"):
        return f"https://www.youtube.com/{ref}"
    else:
        return f"https://www.youtube.com/@{ref}"


async def get_channel_handle(channel_url: str) -> str:
    logger.info(f"Launching browser to get handle from: {channel_url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                locale="en-US",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36")
            page = await context.new_page()

            logger.info(f"Navigating to {channel_url}")
            await page.goto(channel_url, timeout=60000)
            await page.wait_for_selector(HANDLE_ELEMENT, timeout=60000)

            logger.info(f"Looking for handle using selector: {HANDLE_ELEMENT}")
            handle_elem = await page.query_selector(HANDLE_ELEMENT)

            if handle_elem:
                handle = await handle_elem.inner_text()
                logger.info(f"Extracted handle: {handle}")
            else:
                logger.warning("Handle element not found.")
                html_content = await page.content()
                logger.info(f"Full HTML content:\n{html_content}")
                handle = "N/A"

            await browser.close()
            return handle
    except Exception as e:
        logger.error(f"Error extracting handle from {channel_url}: {e}")
        return "N/A"


async def get_channel_external_url(channel_identifier: str) -> Optional[str]:
    logger.info(f"Launching browser to get domain from: {channel_identifier}")
    channel_url = channel_ref_to_url(channel_identifier)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True,
                                  args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                locale="en-US",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36")
            page = await context.new_page()

            await page.goto(channel_url, timeout=30000)
            await page.wait_for_selector(DEFAULT_LINK_SELECTOR, timeout=45000)
            external_url_elem = await page.query_selector(DEFAULT_LINK_SELECTOR)

            if external_url_elem:
                external_url = await external_url_elem.inner_text()
                logger.info(f"Extracted domain: {external_url}")
            else:
                logger.warning("Domain element not found.")
                html_content = await page.content()
                logger.warning(f"Page HTML (full): {html_content}")
                external_url = None

            await browser.close()
            return external_url
    except Exception as e:
        logger.error(f"Error extracting domain from {channel_url}: {e}")
        return None


async def get_featured_channel_links(channel_identifier: str) -> List[str]:
    logger.info(f"Launching browser to extract featured channel links from: {channel_identifier}")
    channel_url = channel_ref_to_url(channel_identifier)
    links = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True,
                                  args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                locale="en-US",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36")
            page = await context.new_page()

            logger.info(f"Navigating to {channel_url}")
            await page.goto(channel_url, timeout=60000)
            await page.wait_for_selector(FEATURED_CHANNEL_SELECTOR, timeout=45000)

            anchor_elements = await page.query_selector_all(FEATURED_CHANNEL_SELECTOR)
            if not anchor_elements:
                logger.warning(f"No featured channel elements found using selector: {FEATURED_CHANNEL_SELECTOR}")
                html_content = await page.content()
                logger.warning(f"Page HTML (full): {html_content}")

            for anchor in anchor_elements:
                href = await anchor.get_attribute('href')
                if href:
                    cleaned = href.lstrip('/')
                    links.append(cleaned)
                    logger.warning(f"Found featured link: {cleaned}")

            await browser.close()
            return links
    except Exception as e:
        logger.error(f"Error extracting featured links from {channel_url}: {e}")
        return []
