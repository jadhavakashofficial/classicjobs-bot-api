import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from youtube_transcript_api import YouTubeTranscriptApi
from utils.load_env import *
from wordpress_draft_creator.create_drafts import create_wordpress_drafts
from youtube_scraper.fetch_latest_videos import fetch_latest_video_info
from youtube_scraper.fetch_comments import fetch_comments
from competitor_scraper.fetch_jobs_from_apis import fetch_jobs_from_all_apis
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# 📂 Ensure training folder exists
os.makedirs("bot_training_logs", exist_ok=True)

def clean_text(text):
    return text.replace('\n', ' ').strip()

def classify_transcript(transcript):
    prompt = (
        "Classify this YouTube transcript into one of the following categories: "
        "job_update, interview_tips, career_faq, resume_tips, motivational. "
        f"\nTranscript:\n{transcript[:1500]}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        return "unclassified"

def run_daily_task():
    print("📺 Fetching latest YouTube videos...")
    videos = fetch_latest_video_info()
    combined_lines = []

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]
        print("🎥", title)

        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
            transcript = clean_text(" ".join([t["text"] for t in transcript_data]))
            comments = fetch_comments(video_id)
            category = classify_transcript(transcript)

            combined_lines.append(
                f"=== {title} ===\nhttps://youtube.com/watch?v={video_id}\n\n"
                f"Category: {category}\n"
                f"Transcript:\n{transcript}\n\nTop Comments:\n" + "\n".join(comments) + "\n\n"
            )

            print(f"✅ Saved: {title} → [{category}]")
        except Exception as e:
            print(f"❌ Skipped {title}: {e}")

    # Save all in one file
    path = "bot_training_logs/daily_combined.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))
    print(f"🗂️ Combined data saved to {path}")

    print("🌐 Fetching competitor job posts...")
    jobs = fetch_jobs_from_all_apis()

    print("📝 Creating draft posts...")
    create_wordpress_drafts(jobs)

# 🚀 Run
if __name__ == "__main__":
    run_daily_task()