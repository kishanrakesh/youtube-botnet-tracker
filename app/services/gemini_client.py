import os
from typing import Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationResponse

from app.utils.logging import get_logger

logger = get_logger(__name__)

# Initialize Gemini model only once
model = GenerativeModel("gemini-1.5-pro")  # or "gemini-1.0-pro" if 1.5 not enabled

def is_name_likely_female(handle_or_name: str) -> bool:
    return False
    # """
    # Uses Gemini to determine whether a handle or string likely includes a female first name.
    # """
    # try:
    #     prompt = (
    #         f"Does the string '{handle_or_name}' appear to contain a real female first name? "
    #         f"Only reply 'Yes' or 'No'. Do not explain."
    #     )

    #     response: GenerationResponse = model.generate_content(prompt)
    #     answer = response.text.strip().lower()

    #     logger.info(f"[Gemini] Name check '{handle_or_name}' → {answer}")

    #     return "yes" in answer
    # except Exception as e:
    #     logger.error(f"Gemini error for handle '{handle_or_name}': {e}")
    #     return False