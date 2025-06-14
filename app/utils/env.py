import os
from dotenv import load_dotenv

# Load .env file in local dev environments
load_dotenv()

# Required Environment Variables
REQUIRED_VARS = [
    "GCP_PROJECT",
    "API_KEY",
    "CSE_ENGINE_ID",
]

# Validate presence of all required variables
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# Access variables via functions
def get_gcp_project() -> str:
    return os.getenv("GCP_PROJECT")

def get_api_key() -> str:
    return os.getenv("API_KEY")

def get_cse_engine_id() -> str:
    return os.getenv("CSE_ENGINE_ID")
