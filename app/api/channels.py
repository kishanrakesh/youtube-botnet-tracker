# app/routes/add_channel.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

from app.services.firestore_client import add_channel_by_id, get_channel_by_id, get_channel_by_handle, create_channel_channel_link, create_video, store_comment, add_domain_entry, create_domain_channel_link, get_all_channel_ids
from app.utils.pattern import extract_video_id, extract_channel_id, extract_domain_from_text
from app.utils.crawler import get_channel_external_url, get_featured_channel_links
from app.services.youtube_client import fetch_channel_metadata_by_id, fetch_channel_metadata_by_handle, fetch_video_metadata, fetch_comments

router = APIRouter()

class AddChannelRequest(BaseModel):
    channel_identifier: str
    source: Optional[str] = None
    notes: Optional[str] = None

class AddVideoRequest(BaseModel):
    video_id: str

class ScanVideoForRequest(BaseModel):
    video_id: str

@router.post("/add_channel")
async def add_channel(request: AddChannelRequest):
    try:
        channel_id,channel_data = await fetch_channel_data_from_id_or_handle(request.channel_identifier, request.source, request.notes)

        external_url = await get_channel_external_url(channel_id)
        if external_url:
            channel_data["external_url"] = external_url
        
        result = await add_channel_by_id(
                channel_id = channel_id,
                channel_data = channel_data
            )
        

        if external_url:
            domain_name = extract_domain_from_text(external_url)
            await add_domain_entry(domain_name, request.source, request.notes)

            channel_domain_link_data = {
                "channel_id": channel_id, 
                "domain_name": domain_name,
            }

            await create_domain_channel_link(channel_domain_link_data)


        featured_channels = await get_featured_channel_links(channel_id)
        
        for url in featured_channels:
            featured_identifier = extract_channel_id(str(url))
            featured_channel_id,featured_channel_data = await fetch_channel_data_from_id_or_handle(featured_identifier, request.source, request.notes)
            
            external_url = await get_channel_external_url(featured_channel_id)
            if external_url:
                featured_channel_data["external_url"] = external_url
            
            await add_channel_by_id(
                channel_id = featured_channel_id,
                channel_data = featured_channel_data
            )

            if external_url:
                domain_name = extract_domain_from_text(external_url)
                await add_domain_entry(domain_name, request.source, request.notes)

                channel_domain_link_data = {
                    "channel_id": featured_channel_id, 
                    "domain_name": domain_name,
                }

                await create_domain_channel_link(channel_domain_link_data)
            
            channel_channel_link_data = {
                "source_channel_id": channel_id, 
                "target_channel_id": featured_channel_id,
                "relationship_type": "featured"
            }

            await create_channel_channel_link(channel_channel_link_data)
        
        return {"status": "success", "channel": result}

        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add channel: {e}")


async def build_channel_data_from_api(raw_channel_data, source, notes):
    raw_channel_data_snippet = raw_channel_data["snippet"]
    handle = raw_channel_data_snippet["customUrl"]
    raw_channel_data_statistics = raw_channel_data["statistics"]
    
    channel_statistics = {
        "view_count": raw_channel_data_statistics["viewCount"],
        "subscriber_count": raw_channel_data_statistics["subscriberCount"],
        "video_count": raw_channel_data_statistics["videoCount"]
    }

    channel_data = {
        "channel_id": raw_channel_data["id"],
        "handle": handle,
        "source": source,
        "notes": notes,
        "title": raw_channel_data_snippet["title"],
        "description": raw_channel_data_snippet["description"],
        "created_at": raw_channel_data_snippet["publishedAt"],
        "thumbnail_url": raw_channel_data_snippet["thumbnails"]["default"]["url"],
        "statistics": channel_statistics,
    }

    return channel_data




async def fetch_channel_data_from_id_or_handle(channel_identifier, source, notes):
    
    if channel_identifier.startswith("@"):

        handle = channel_identifier

        # channel_id, channel_data = await get_channel_by_handle(handle)
        # if channel_data:
        #     return (channel_id, channel_data)  # Or update if needed
        
        raw_channel_data = await fetch_channel_metadata_by_handle(handle)
        channel_id = raw_channel_data["id"]
    
    elif channel_identifier:

        channel_id = channel_identifier

        # _,channel_data = await get_channel_by_id(channel_id)
        # if channel_data:
        #     return (channel_id, channel_data)  # Or update if needed
        
        raw_channel_data = await fetch_channel_metadata_by_id(channel_identifier)
        
    else:
        raise HTTPException(status_code=500, detail=f"Unable to find channel identifier")
    
    channel_data = await build_channel_data_from_api(raw_channel_data, source, notes)
    
    return (channel_id, channel_data)

async def scan_video_and_store_channel_comments(video_id: str) -> Optional[List]:
    """
    Searches for a comment by a specific channel on a specific video.
    If found, stores it in Firestore and returns the comment.
    """
    comments = await fetch_comments(video_id)
    for comment in comments:
        print(comment["snippet"]["authorDisplayName"] + " - " + comment["snippet"]["authorChannelUrl"])
    channel_id_list = await get_all_channel_ids()
    channel_id_set = set(channel_id_list)
    channel_comments = []
    if comments:
        for comment in comments:
            channel_id = comment["snippet"]["authorChannelId"]["value"]
            if channel_id in channel_id_set:
                comment_snippet = comment["snippet"]
                posted_at = comment_snippet["publishedAt"]
                comment_id = comment.get("id", f"{video_id}_{channel_id}_{posted_at}")
                comment_data = {
                    "comment_id": comment_id,
                    "video_id": video_id,
                    "channel_id": channel_id,
                    "text": comment_snippet["textDisplay"],
                    "like_count": comment_snippet["likeCount"],
                    "posted_at": posted_at
                }
                await store_comment(comment_id, comment_data)

                channel_comments.append(comment)

    return channel_comments


@router.post("/add_video")
async def add_video(request: AddVideoRequest):
    try:
        video_id = request.video_id
        video_data = await add_video_by_video_id(video_id)
        return {"status": "success", "video_data": video_data}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add video: {e}")
    
async def add_video_by_video_id(video_id: str):
    try:
        raw_video_data = await fetch_video_metadata(video_id)
        raw_video_data_snippet = raw_video_data["snippet"]
        raw_video_data_statistics = raw_video_data["statistics"]
        video_topic_list = raw_video_data["topicDetails"]["topicCategories"]

        video_statistics = {
            "view_count": raw_video_data_statistics["viewCount"],
            "like_count": raw_video_data_statistics["likeCount"],
            "comment_count": raw_video_data_statistics["commentCount"],
        }
        
        
        video_data = {
            "video_id": video_id,
            "channel_id": raw_video_data_snippet["channelId"],
            "created_at": raw_video_data_snippet["publishedAt"],
            "title": raw_video_data_snippet["title"],
            "description": raw_video_data_snippet["description"],
            "thumbnail_url": raw_video_data_snippet["thumbnails"]["default"]["url"],
            "category_id": raw_video_data_snippet["categoryId"],
            "statistics": video_statistics,
            "topic_list": video_topic_list
        }

        if "tags" in raw_video_data_snippet:
            video_data["tag_list"] = raw_video_data_snippet["tags"]

        await create_video(video_id, video_data)


        return video_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add video: {e}")
    

    

@router.post("/scan_video_for_comments")
async def scan_video_for_comments(request: ScanVideoForRequest):
    try:
        comments = await scan_video_and_store_channel_comments(request.video_id)
        if comments:
            await add_video_by_video_id(request.video_id)
        return {"status": "success", "video_data": comments}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add video: {e}")

async def add_channel_logic(request: dict):
    try:
        channel_id,channel_data = await fetch_channel_data_from_id_or_handle(request.channel_identifier, request.source, request.notes)

        external_url = await get_channel_external_url(channel_id)
        if external_url:
            channel_data["external_url"] = external_url
        
        result = await add_channel_by_id(
                channel_id = channel_id,
                channel_data = channel_data
            )
        

        if external_url:
            domain_name = extract_domain_from_text(external_url)
            await add_domain_entry(domain_name, request.source, request.notes)

            channel_domain_link_data = {
                "channel_id": channel_id, 
                "domain_name": domain_name,
            }

            await create_domain_channel_link(channel_domain_link_data)


        featured_channels = await get_featured_channel_links(channel_id)
        
        for url in featured_channels:
            featured_identifier = extract_channel_id(str(url))
            featured_channel_id,featured_channel_data = await fetch_channel_data_from_id_or_handle(featured_identifier, request.source, request.notes)
            
            external_url = await get_channel_external_url(featured_channel_id)
            if external_url:
                featured_channel_data["external_url"] = external_url
            
            await add_channel_by_id(
                channel_id = featured_channel_id,
                channel_data = featured_channel_data
            )

            if external_url:
                domain_name = extract_domain_from_text(external_url)
                await add_domain_entry(domain_name, request.source, request.notes)

                channel_domain_link_data = {
                    "channel_id": featured_channel_id, 
                    "domain_name": domain_name,
                }

                await create_domain_channel_link(channel_domain_link_data)
            
            channel_channel_link_data = {
                "source_channel_id": channel_id, 
                "target_channel_id": featured_channel_id,
                "relationship_type": "featured"
            }

            await create_channel_channel_link(channel_channel_link_data)
        
        return {"status": "success", "channel": result}

        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add channel: {e}")
    
@router.post("/update_all_stored_channels")
async def update_all_stored_channels():
    channel_id_list = await get_all_channel_ids()
    for channel_id in channel_id_list:
        print(channel_id)
        try:
            channel_id,channel_data = await fetch_channel_data_from_id_or_handle(channel_id, "update_stored_channels", "update_stored_channels")

            external_url = await get_channel_external_url(channel_id)
            if external_url:
                channel_data["external_url"] = external_url
            
            result = await add_channel_by_id(
                    channel_id = channel_id,
                    channel_data = channel_data
                )
            

            if external_url:
                domain_name = extract_domain_from_text(external_url)
                await add_domain_entry(domain_name, "update_stored_channels", "update_stored_channels")

                channel_domain_link_data = {
                    "channel_id": channel_id, 
                    "domain_name": domain_name,
                }

                await create_domain_channel_link(channel_domain_link_data)


            featured_channels = await get_featured_channel_links(channel_id)
            
            for url in featured_channels:
                featured_identifier = extract_channel_id(str(url))
                featured_channel_id,featured_channel_data = await fetch_channel_data_from_id_or_handle(featured_identifier, "update_stored_channels", "update_stored_channels")
                
                external_url = await get_channel_external_url(featured_channel_id)
                if external_url:
                    featured_channel_data["external_url"] = external_url
                
                await add_channel_by_id(
                    channel_id = featured_channel_id,
                    channel_data = featured_channel_data
                )

                if external_url:
                    domain_name = extract_domain_from_text(external_url)
                    await add_domain_entry(domain_name, "update_stored_channels", "update_stored_channels")

                    channel_domain_link_data = {
                        "channel_id": featured_channel_id, 
                        "domain_name": domain_name,
                    }

                    await create_domain_channel_link(channel_domain_link_data)
                
                channel_channel_link_data = {
                    "source_channel_id": channel_id, 
                    "target_channel_id": featured_channel_id,
                    "relationship_type": "featured"
                }

                await create_channel_channel_link(channel_channel_link_data)

            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add channel: {e}")
    return {"status": "success", "channel": result}


import csv
import os

CSV_FILE = "video_comment_channels.csv"

@router.post("/scan_video_and_fetch_channel_urls")
async def scan_video_and_fetch_channel_urls(request: ScanVideoForRequest) -> Optional[List[str]]:
    comments = await fetch_comments(request.video_id)            # Your existing helper

    # Create file if it doesn’t exist and write header once
    file_exists = os.path.isfile(CSV_FILE)

    channel_urls: List[str] = []

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["author_channel_url", "author_display_name", "like_count", "reply_count", "text_display", "is_bot"])

        for comment in comments:
            name = comment["snippet"]["authorDisplayName"]
            channel_url = comment["snippet"]["authorChannelUrl"]
            like_count = comment["snippet"]["likeCount"]
            reply_count = comment["totalReplyCount"]
            text_display = comment["snippet"]["textDisplay"]
            writer.writerow([channel_url, name, like_count, reply_count, text_display, ""])
            channel_urls.append(channel_url)             # keep in memory if needed

                # Optional: log as you go
                # print(f"Saved: {name} - {channel_url}")

    return channel_urls