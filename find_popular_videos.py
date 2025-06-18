from googleapiclient.discovery import build

api_key = "AIzaSyADvDBHXJNthXmEcWPJA2HtrpsEX3dQnNQ"
youtube = build("youtube", "v3", developerKey=api_key)

videos_from_categories = []
videos_from_trending = []
next_token = None

assignable_category_ids = [
    "1",   # Film & Animation
    "2",   # Autos & Vehicles
    "10",  # Music
    "15",  # Pets & Animals
    "17",  # Sports
    # "19",  # Travel & Events
    "20",  # Gaming
    "22",  # People & Blogs
    "23",  # Comedy
    "24",  # Entertainment
    "25",  # News & Politics
    "26",  # Howto & Style
    # "27",  # Education
    "28",  # Science & Technology
    "29",  # Nonprofits & Activism
]



for i in range(45):
    next_token = None
    try:
        while True:
            req = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="US",
                maxResults=50,
                videoCategoryId=i,
                pageToken=next_token
            )
            res = req.execute()
            videos_from_categories.extend(res["items"])
            next_token = res.get("nextPageToken")
            if not next_token:
                break
        print(f"✅ Fetched videos from category {i}")
    except Exception as e:
        print(f"⚠️ Skipping category {i}: {e}")

while True:
    req = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode="US",
        maxResults=50,
        pageToken=next_token
    )
    res = req.execute()
    videos_from_trending.extend(res["items"])
    next_token = res.get("nextPageToken")
    if not next_token:
        break

print("Fetched", len(videos_from_trending), "videos_from_trending (approx total:", res["pageInfo"]["totalResults"], ")")


# Extract video IDs from each list
ids_from_categories = {video["id"] for video in videos_from_categories}
ids_from_trending = {video["id"] for video in videos_from_trending}

# Find intersection
common_ids = ids_from_categories.intersection(ids_from_trending)

# Print results
print(f"\nTotal unique videos from categories: {len(ids_from_categories)}")
print(f"Total unique videos from trending: {len(ids_from_trending)}")
print(f"Total overlapping videos: {len(common_ids)}")

# Optional: Show percentage overlap
percent_overlap = len(common_ids) / len(ids_from_trending) * 100 if ids_from_trending else 0
print(f"Overlap percentage (of trending videos): {percent_overlap:.2f}%")