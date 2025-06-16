from google.cloud import firestore
from typing import Dict, Optional, List
from datetime import datetime
import os
from google.cloud.firestore import SERVER_TIMESTAMP

from app.config import (
    COLLECTION_CHANNELS,
    COLLECTION_DOMAINS,
    COLLECTION_VIDEOS,
    COLLECTION_COMMENTS,
    FIELD_CREATED_AT,
    FIELD_UPDATED_AT,
    FIELD_DISCOVERED_AT,
    COLLECTION_CHANNEL_DOMAIN_LINK,
    COLLECTION_CHANNEL_CHANNEL_LINK,
    COLLECTION_CHANNEL_VIDEO_COMMENT
)


def get_firestore_client():
    return firestore.Client(project=os.getenv("GCP_PROJECT"))


# === CHANNELS ===

async def get_channel_by_id(channel_id: str) -> tuple:
    db = get_firestore_client()
    doc = db.collection(COLLECTION_CHANNELS).document(channel_id).get()
    return (doc.id,doc.to_dict()) if doc.exists else (None, None)

async def get_channel_by_handle(handle: str) -> Optional[tuple]:
    db = get_firestore_client()
    query = db.collection(COLLECTION_CHANNELS).where("handle", "==", handle).limit(1)
    docs = query.stream()
    for doc in docs:
        return (doc.id,doc.to_dict())
    return (None, None)

async def update_channel_by_id(channel_id: str, data: Dict):
    db = get_firestore_client()
    data[FIELD_UPDATED_AT] = datetime.utcnow().isoformat() + "Z"
    db.collection(COLLECTION_CHANNELS).document(channel_id).set(data, merge=True)


async def create_channel(channel_id: str, data: Dict):
    db = get_firestore_client()
    data[FIELD_DISCOVERED_AT] = datetime.utcnow().isoformat() + "Z"
    data[FIELD_UPDATED_AT] = datetime.utcnow().isoformat() + "Z"
    db.collection(COLLECTION_CHANNELS).document(channel_id).set(data)

# app/services/firestore.py (continued)

async def add_channel_by_id(
    channel_id: str,
    channel_data: Dict,
) -> Dict:

    await create_channel(channel_id, channel_data)

    # if video_id:
    #     video_data = {"channel_id": channel_id}
    #     await create_video(video_id, video_data)

    return channel_data

async def get_all_bot_channel_ids() -> List[str]:
    db = get_firestore_client()
    docs = db.collection(COLLECTION_CHANNELS).where("is_bot", "==", True).stream()
    return [doc.id for doc in docs]

async def create_channel_channel_link(data: Dict) -> List[str]:
    db = get_firestore_client()
    data[FIELD_DISCOVERED_AT] = datetime.utcnow().isoformat() + "Z"
    db.collection(COLLECTION_CHANNEL_CHANNEL_LINK).document(data["source_channel_id"] + "::" + data["target_channel_id"]).set(data)


async def get_all_channel_ids() -> List[str]:
    """
    Retrieves all channel IDs from the 'channels' collection using only document IDs.
    """
    db = get_firestore_client()
    collection_ref = db.collection("channels")
    docs = collection_ref.list_documents()  # Async iterable of DocumentReferences

    return [doc.id for doc in docs]

# === DOMAINS ===

async def create_domain(domain_name: str, data: Dict):
    db = get_firestore_client()
    data[FIELD_CREATED_AT] = datetime.utcnow().isoformat()
    db.collection(COLLECTION_DOMAINS).document(domain_name).set(data)


async def get_domain_by_name(domain_name: str) -> Optional[Dict]:
    db = get_firestore_client()
    doc = db.collection(COLLECTION_DOMAINS).document(domain_name).get()
    return doc.to_dict() if doc.exists else None


async def update_domain(domain_name: str, data: Dict):
    db = get_firestore_client()
    data[FIELD_UPDATED_AT] = datetime.utcnow().isoformat()
    db.collection(COLLECTION_DOMAINS).document(domain_name).set(data, merge=True)

async def add_domain_entry(domain: str, source: Optional[str] = None, notes: Optional[str] = None) -> Dict:
    existing = await get_domain_by_name(domain)
    if existing:
        return existing  # Optionally update instead if needed

    domain_data = {
        "domain": domain,
        "source": source,
        "notes": notes,
        "active": True,
    }
    await create_domain(domain, domain_data)
    return domain_data

async def get_all_domains_from_firestore() -> List[str]:
    """
    Retrieve a list of all domain document IDs from Firestore.
    """
    db = get_firestore_client()
    domain_docs = db.collection(COLLECTION_DOMAINS).stream()
    domain_names = [doc.id for doc in domain_docs]
    return domain_names

async def create_domain_from_text() -> List[str]:
    #TODO
    pass

async def create_domain_channel_link(data: Dict) -> List[str]:
    db = get_firestore_client()
    data[FIELD_DISCOVERED_AT] = datetime.utcnow().isoformat() + "Z"
    db.collection(COLLECTION_CHANNEL_DOMAIN_LINK).document(data["domain_name"] + "::" + data["channel_id"]).set(data)



# === VIDEOS ===

async def create_video(video_id: str, data: Dict):
    db = get_firestore_client()
    data[FIELD_DISCOVERED_AT] = datetime.utcnow().isoformat()
    db.collection(COLLECTION_VIDEOS).document(video_id).set(data)


async def get_video_by_id(video_id: str) -> Optional[Dict]:
    db = get_firestore_client()
    doc = db.collection(COLLECTION_VIDEOS).document(video_id).get()
    return doc.to_dict() if doc.exists else None


# === COMMENTS ===

async def store_comment(comment_id, data: Dict):
    db = get_firestore_client()
    data[FIELD_DISCOVERED_AT] = datetime.utcnow().isoformat() + "Z"
    db.collection(COLLECTION_CHANNEL_VIDEO_COMMENT).document(comment_id).set(data)