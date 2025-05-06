import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from googleapiclient.discovery import build
from utils.load_env import YOUTUBE_API_KEY, COMPETITOR_YT_CHANNELS

# ✅ Get YouTube API service
def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# ✅ Fetch latest video from a single channel
def fetch_latest_video_id(channel_id):
    youtube = get_youtube_service()
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=1,
        order="date",
        type="video"
    )
    response = request.execute()
    item = response["items"][0]
    return {
        "channel_id": channel_id,
        "title": item["snippet"]["title"],
        "video_id": item["id"]["videoId"],
        "published_at": item["snippet"]["publishedAt"]
    }

# ✅ Collect latest unique videos from all channels
def fetch_latest_video_info():
    seen_video_ids = set()
    results = []

    for cid in COMPETITOR_YT_CHANNELS:  # ← NO split() here anymore
        video = fetch_latest_video_id(cid.strip())
        if video["video_id"] not in seen_video_ids:
            seen_video_ids.add(video["video_id"])
            results.append(video)
        else:
            print(f"⚠️ Duplicate video skipped: {video['title']}")

    return results

# ✅ Manual test
if __name__ == "__main__":
    latest_videos = fetch_latest_video_info()
    for video in latest_videos:
        print(f"{video['published_at']} - {video['title']} → https://youtube.com/watch?v={video['video_id']}")