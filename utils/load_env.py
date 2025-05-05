import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COMPETITOR_YT_CHANNELS = os.getenv("COMPETITOR_YT_CHANNELS", "").split(",")

COMPETITOR_JOB_APIS = [
    os.getenv("COMPETITOR_JOB_API_1"),
    os.getenv("COMPETITOR_JOB_API_2"),
    os.getenv("COMPETITOR_JOB_API_3"),
    os.getenv("COMPETITOR_JOB_API_4"),
]

# ✅ Add these to support WordPress posting
WORDPRESS_SITE = os.getenv("WORDPRESS_SITE")
WORDPRESS_USER = os.getenv("WORDPRESS_USER")
WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD")
CLASSIC_TECH_YT_CHANNEL = os.getenv("CLASSIC_TECH_YT_CHANNEL")