import re
from urllib.parse import urlparse, parse_qs

class ExtractionError(ValueError):
    pass

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, shortened, and embed formats.
    """
    parsed = urlparse(url)

    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        elif "/embed/" in parsed.path:
            return parsed.path.split("/embed/")[-1].split("/")[0]
    elif "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    raise ExtractionError(f"Could not extract video ID from URL: {url}")


def extract_channel_id(url: str) -> str:
    """
    Extracts the channel ID or handle from a YouTube channel URL.
    Supports /channel/, /user/, or @handle URLs, including subpaths like /about.
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    if not path_parts:
        raise ExtractionError(f"Empty path in URL: {url}")

    if path_parts[0].startswith("@"):
        return path_parts[0]  # Handle (e.g., @bot123)
    elif path_parts[0] in {"channel", "user"} and len(path_parts) >= 2:
        return path_parts[1]  # e.g., channel/UCL123/about → UCL123
    else:
        raise ExtractionError(f"Could not extract channel ID from URL: {url}")


def extract_domain_from_text(text: str) -> str:
    """
    Extracts the first domain-like string from a snippet of text.
    Used in Google CSE snippet parsing.
    """
    match = re.search(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b", text)
    if match:
        return match.group(0)
    raise ExtractionError("No domain found in input text.")
