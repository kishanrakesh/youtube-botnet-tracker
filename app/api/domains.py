
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.firestore_client import add_domain_entry

router = APIRouter()

class AddDomainRequest(BaseModel):
    domain: str
    source: Optional[str] = None
    notes: Optional[str] = None

@router.post("/")
async def add_domain(request: AddDomainRequest):
    try:
        result = await add_domain_entry(
            domain=request.domain,
            source=request.source,
            notes=request.notes
        )
        return {"status": "success", "domain": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add domain: {e}")