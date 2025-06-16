from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="YouTube Botnet Tracker",
    description="API for tracking and analyzing YouTube bot networks",
    version="1.0.0"
)

# Register route modules
from app.api import (
    channels,
    domains,
    scan_comments,
    discover_sinks,
    health,
)

app.include_router(health.router, tags=["Health"])
app.include_router(domains.router, prefix="/domain", tags=["Domain"])
app.include_router(channels.router, prefix="/channel", tags=["Channel"])
app.include_router(discover_sinks.router, prefix="/discover", tags=["Discovery"])
app.include_router(scan_comments.router, prefix="/comments", tags=["Comments"])