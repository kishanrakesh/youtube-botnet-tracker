# === Firestore Collection Names ===
COLLECTION_DOMAINS = "domains"
COLLECTION_CHANNELS = "channels"
COLLECTION_VIDEOS = "videos"
COLLECTION_COMMENTS = "comments"

# === Firestore Field Names ===
FIELD_CREATED_AT = "created_at"
FIELD_UPDATED_AT = "updated_at"
FIELD_INACTIVE = "inactive"

# === External APIs ===
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
CSE_API_BASE = "https://www.googleapis.com/customsearch/v1"

# === Limits & Defaults ===
YOUTUBE_COMMENTS_PAGE_LIMIT = 5         # Pages to scan per video
CSE_RESULTS_PER_DOMAIN = 5              # Results to fetch per domain
CHANNEL_ENRICH_BATCH_SIZE = 20          # Max batch size for API calls
SINK_DISCOVERY_BATCH_LIMIT = 10         # Domains per discovery batch
MAX_FEATURED_CHANNELS = 50              # Optional cap if needed

# === Time Constants ===
ONE_DAY_SECONDS = 86400
ONE_WEEK_SECONDS = 604800