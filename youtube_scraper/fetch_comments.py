import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from googleapiclient.discovery import build
from utils.load_env import YOUTUBE_API_KEY

def get_youtube_service():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_comments(video_id, max_results=50):
    youtube = get_youtube_service()
    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
    except Exception as e:
        print(f"⚠️ Could not fetch comments for {video_id}: {e}")

    return comments

# Test run
if __name__ == "__main__":
    test_video_id = "kJlqJfLbG3Y"  # Replace with any real video ID
    comments = fetch_comments(test_video_id)
    print(f"🗨️ {len(comments)} comments fetched.")
    for c in comments[:5]:
        print("—", c)
