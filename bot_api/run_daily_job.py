import os
import sys
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# ✅ Fix for relative import to work on GitHub Actions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.load_env import *
from wordpress_draft_creator.create_drafts import create_wordpress_drafts
from youtube_scraper.fetch_latest_videos import fetch_latest_video_info
from youtube_scraper.fetch_comments import fetch_comments
from competitor_scraper.fetch_jobs_from_apis import fetch_competitor_jobs
from youtube_scraper.analyze_and_classify import classify_transcript

# Ensure log folder exists
os.makedirs("bot_training_logs", exist_ok=True)

def clean_text(text):
    return text.replace('\n', ' ').strip()

def save_to_logs(category, video_id, transcript, comments):
    path = f"bot_training_logs/{category}_{video_id}.txt"
    if os.path.exists(path):
        return  # Skip duplicates
    with open(path, "w", encoding="utf-8") as f:
        f.write("Transcript:\n" + transcript + "\n\n")
        f.write("Top Comments:\n" + "\n".join(comments))

def run_daily_task():
    print("📺 Fetching latest YouTube videos...")
    all_videos = fetch_latest_video_info()

    for video in all_videos:
        video_id = video["video_id"]
        title = video["title"]
        url = f"https://youtube.com/watch?v={video_id}"

        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
            transcript = clean_text(" ".join([item["text"] for item in transcript_data]))
            comments = fetch_comments(video_id)
            category = classify_transcript(transcript)
            save_to_logs(category, video_id, transcript, comments)
            print(f"✅ Saved: {title} [{category}]")
        except Exception as e:
            print(f"❌ Skipped {title}: {e}")

    print("🌐 Fetching competitor job posts...")
    jobs = fetch_competitor_jobs()

    print("📝 Drafting new jobs...")
    create_wordpress_drafts(jobs)

if __name__ == "__main__":
    run_daily_task()
