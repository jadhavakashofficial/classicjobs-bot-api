import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from googleapiclient.discovery import build
from utils.load_env import YOUTUBE_API_KEY, COMPETITOR_YT_CHANNELS

from datetime import datetime

def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_videos_by_year(year=2020):
    seen_video_ids = set()
    results = []

    published_after = f"{year}-01-01T00:00:00Z"
    published_before = f"{year}-12-31T23:59:59Z"

    for cid in COMPETITOR_YT_CHANNELS:
        youtube = get_youtube_service()
        request = youtube.search().list(
            part="snippet",
            channelId=cid.strip(),
            maxResults=50,
            order="date",
            type="video",
            publishedAfter=published_after,
            publishedBefore=published_before
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            if video_id not in seen_video_ids:
                seen_video_ids.add(video_id)
                results.append({
                    "channel_id": cid,
                    "title": item["snippet"]["title"],
                    "video_id": video_id,
                    "published_at": item["snippet"]["publishedAt"]
                })

    return results

if __name__ == "__main__":
    videos = fetch_videos_by_year(2020)
    for v in videos:
        print(f"{v['published_at']} | {v['title']} → https://youtube.com/watch?v={v['video_id']}")