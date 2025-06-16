import base64
import httpx
import logging
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

# Create a single Vision API client instance
client = vision.ImageAnnotatorClient()

async def is_profile_image_flagged(image_url: str) -> bool:
    """
    Uses Google Cloud Vision API to detect if a profile image is flagged as 'racy' or 'adult'.
    Returns True if either likelihood is 'LIKELY' or above.
    """

    try:
        # Use Vision API with image URI
        image = vision.Image()
        image.source.image_uri = image_url

        response = client.safe_search_detection(image=image)
        safe = response.safe_search_annotation

        if response.error.message:
            raise GoogleAPIError(response.error.message)

        logger.info(f"SafeSearch for {image_url} => adult={safe.adult}, racy={safe.racy}")

        # Define what counts as inappropriate
        flagged_likelihoods = {"LIKELY", "VERY_LIKELY"}

        return safe.adult in flagged_likelihoods or safe.racy in flagged_likelihoods

    except GoogleAPIError as e:
        logger.warning(f"Vision API error on image {image_url}: {e}")
        return False
    except Exception as e:
        logger.warning(f"Unknown error while checking image {image_url}: {e}")
        return False
