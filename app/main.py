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
    add_domain,
    add_channel,
    scan_comments,
    discover_sinks,
    health,
)

app.include_router(health.router, tags=["Health"])
app.include_router(add_domain.router, prefix="/domain", tags=["Domain"])
app.include_router(add_channel.router, prefix="/channel", tags=["Channel"])
app.include_router(discover_sinks.router, prefix="/discover", tags=["Discovery"])
app.include_router(scan_comments.router, prefix="/comments", tags=["Comments"])