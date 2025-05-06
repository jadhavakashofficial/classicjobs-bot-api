import requests
from utils.load_env import YOUTUBE_API_KEY, CLASSIC_TECH_YT_CHANNEL

def fetch_classictech_video(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": CLASSIC_TECH_YT_CHANNEL,
        "q": query,
        "maxResults": 1,
        "order": "relevance",
        "type": "video",
        "key": YOUTUBE_API_KEY,
    }

    try:
        r = requests.get(url, params=params)
        items = r.json().get("items")
        if items:
            video = items[0]
            title = video["snippet"]["title"]
            video_id = video["id"]["videoId"]
            link = f"https://youtube.com/watch?v={video_id}"
            return title, link
    except Exception as e:
        print("❌ YouTube fetch failed:", e)

    return None, None
