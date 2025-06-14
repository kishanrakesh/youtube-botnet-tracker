from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.services.cse import discover_sink_channels_for_domains
from app.services.firestore_client import create_channel, get_all_domains_from_firestore
from app.utils.extract import extract_channel_id

router = APIRouter()

class DiscoverSinksRequest(BaseModel):
    domains: Optional[List[str]] = None  # If None, pull all from Firestore

@router.post("/")
async def discover_sinks(request: DiscoverSinksRequest):
    try:
        # Use user-specified domains or pull all domains from Firestore
        domain_names = request.domains or await get_all_domains_from_firestore()


        if not domain_names:
            raise HTTPException(status_code=400, detail="No domains provided or found in Firestore.")


        all_discovered = []
        for domain in domain_names:
            discovered_channels = await discover_sink_channels_for_domains(domain)
            for ch in discovered_channels:
                ch_id = extract_channel_id(ch["link"])
                await create_channel(ch_id, {
                    "linked_domain": domain,
                    "source": "cse_discovery",
                    "notes": f"Discovered via CSE for domain: {domain}"
                })
            all_discovered.extend(discovered_channels)

        return {
            "status": "success",
            "domains_searched": len(domain_names),
            "channels_discovered": len(all_discovered),
            "channels_stored": len(all_discovered)  # 1:1 for now
        }

    except Exception as e:
        print(f"[ERROR] {e}")  # Add this line
        raise HTTPException(status_code=500, detail=f"Sink discovery failed: {e}")
