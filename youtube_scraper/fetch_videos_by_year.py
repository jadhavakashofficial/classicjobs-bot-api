import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from googleapiclient.discovery import build
from utils.load_env import YOUTUBE_API_KEY, COMPETITOR_YT_CHANNELS, CLASSIC_TECH_YT_CHANNEL

def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_videos_by_year(year):
    all_videos = []
    seen = set()

    # Use COMPETITOR_YT_CHANNELS directly if it's already a list
    all_channels = COMPETITOR_YT_CHANNELS + [CLASSIC_TECH_YT_CHANNEL]

    for channel_id in all_channels:
        youtube = get_youtube_service()
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id.strip(),
            maxResults=50,
            order="date",
            type="video",
            publishedAfter=f"{year}-01-01T00:00:00Z",
            publishedBefore=f"{year}-12-31T23:59:59Z"
        )
        response = request.execute()
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            if video_id not in seen:
                seen.add(video_id)
                all_videos.append({
                    "channel_id": channel_id,
                    "title": item["snippet"]["title"],
                    "video_id": video_id,
                    "published_at": item["snippet"]["publishedAt"]
                })

    return all_videos

# Optional test
if __name__ == "__main__":
    videos = fetch_videos_by_year(2020)
    print(f"Total videos found: {len(videos)}")
    for v in videos:
        print(v["title"], "-", v["published_at"])