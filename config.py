import os
from datetime import datetime

NAME_FORMAT = os.getenv(
    "NAME_FORMAT",
    "{title} - S{season:02}E{episode:02} [{quality}] [{audio_codec}-{audio_channels}ch].{ext}"
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
USE_S3 = os.getenv("USE_S3", "0") == "1"
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
S3_ACL = os.getenv("S3_ACL", "private")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./animekaidl.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

AUTO_DETECT_AUDIO = os.getenv("AUTO_DETECT_AUDIO", "1") == "1"
API_KEY = os.getenv("API_KEY", "")

ONGOING_PREFIX = os.getenv("ONGOING_PREFIX", "ongoing")
ONGOING_NOTIFY = os.getenv("ONGOING_NOTIFY", "0") == "1"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

ALLOWED_EXTENSIONS = set(
    [
        e.strip().lower()
        for e in os.getenv(
            "ALLOWED_EXTENSIONS",
            "mkv,mp4,avi,webm"
        ).split(",")
        if e.strip()
    ]
)

MAX_UPLOAD_SIZE = int(
    os.getenv(
        "MAX_UPLOAD_SIZE",
        2 * 1024 * 1024 * 1024
    )
)

UPLOADED_AT_FORMAT = os.getenv(
    "UPLOADED_AT_FORMAT",
    "%Y-%m-%dT%H%M%SZ"
)