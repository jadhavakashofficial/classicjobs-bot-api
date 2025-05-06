import os
import sys
import calendar
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from youtube_scraper.fetch_comments import fetch_comments
from utils.load_env import YOUTUBE_API_KEY, COMPETITOR_YT_CHANNELS

OUTPUT_DIR = "competitor_training_logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_videos(channel_id, published_after, published_before):
    youtube = get_youtube_service()
    videos = []
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        order="date",
        type="video",
        publishedAfter=published_after,
        publishedBefore=published_before
    )
    response = request.execute()
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"]
        })
    return videos

def clean_text(text):
    return text.replace('\n', ' ').strip()

def process_video(video_id, title):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
        transcript = clean_text(" ".join([t["text"] for t in transcript_data]))
        comments = fetch_comments(video_id)
        return f"=== {title} ===\nhttps://youtube.com/watch?v={video_id}\n\nTranscript:\n{transcript}\n\nTop Comments:\n" + "\n".join(comments) + "\n\n"
    except Exception as e:
        print(f"❌ Skipped {title}: {e}")
        return None

def collect_monthly_data_2021():
    channels = COMPETITOR_YT_CHANNELS.split(",") if isinstance(COMPETITOR_YT_CHANNELS, str) else COMPETITOR_YT_CHANNELS

    for month in range(2, 13):  # Feb to Dec
        filename = f"{OUTPUT_DIR}/2021-{month:02}.txt"
        if os.path.exists(filename):
            print(f"📁 Already exists: {filename}")
            continue

        print(f"📦 Collecting data for 2021-{month:02}")
        month_data = []

        start_date = f"2021-{month:02}-01T00:00:00Z"
        last_day = calendar.monthrange(2021, month)[1]
        end_date = f"2021-{month:02}-{last_day}T23:59:59Z"

        for channel_id in channels:
            videos = fetch_videos(channel_id.strip(), start_date, end_date)
            for video in videos:
                print("🎥", video["title"])
                content = process_video(video["video_id"], video["title"])
                if content:
                    month_data.append(content)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(month_data))

        print(f"✅ Saved: {filename}")

if __name__ == "__main__":
    collect_monthly_data_2021()