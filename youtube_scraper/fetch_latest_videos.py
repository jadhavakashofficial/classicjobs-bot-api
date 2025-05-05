import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from googleapiclient.discovery import build
from utils.load_env import YOUTUBE_API_KEY, COMPETITOR_YT_CHANNELS

def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

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

def fetch_all_latest_videos():
    seen_video_ids = set()
    results = []

    for cid in COMPETITOR_YT_CHANNELS:
        video = fetch_latest_video_id(cid.strip())
        if video["video_id"] not in seen_video_ids:
            seen_video_ids.add(video["video_id"])
            results.append(video)
        else:
            print(f"⚠️ Duplicate video skipped: {video['title']}")

    return results

# Test it
if __name__ == "__main__":
    latest_videos = fetch_all_latest_videos()
    for video in latest_videos:
        print(f"{video['published_at']} - {video['title']} (https://youtube.com/watch?v={video['video_id']})")
