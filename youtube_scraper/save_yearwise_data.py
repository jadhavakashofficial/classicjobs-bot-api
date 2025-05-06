import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_scraper.fetch_by_year import fetch_videos_by_year
from youtube_scraper.fetch_comments import fetch_comments
from utils.load_env import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY
os.makedirs("bot_training_logs", exist_ok=True)

# 🧹 Clean text
def clean_text(text):
    return text.replace("\n", " ").strip()

# 🧠 Classify transcript content
def classify_transcript(transcript):
    prompt = (
        "Classify this YouTube transcript into one of the following: "
        "job_update, interview_tips, career_faq, resume_tips, motivational. "
        f"\nTranscript:\n{transcript[:1500]}"
    )
    try:
        chat = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content.strip().lower()
    except Exception as e:
        print("❌ Classification failed:", e)
        return "unclassified"

# 💾 Save transcript and comments
def save_to_logs(category, video_id, transcript, comments):
    path = f"bot_training_logs/{category}_{video_id}.txt"
    if os.path.exists(path): return
    with open(path, "w", encoding="utf-8") as f:
        f.write("Transcript:\n" + transcript + "\n\n")
        f.write("Top Comments:\n" + "\n".join(comments))

# 🚀 Collect & save for all videos of a year
def collect_and_save(year=2020):
    print(f"📥 Collecting videos from {year}...")
    videos = fetch_videos_by_year(year)

    for video in videos:
        video_id = video["video_id"]
        title    = video["title"]
        print("🎥", title)

        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
            transcript = clean_text(" ".join([t["text"] for t in transcript_data]))
            comments   = fetch_comments(video_id)
            category   = classify_transcript(transcript)
            save_to_logs(category, video_id, transcript, comments)
            print(f"✅ Saved {title} → {category}")
        except Exception as e:
            print(f"❌ Skipped {title}: {e}")

if __name__ == "__main__":
    collect_and_save(2020)  # 👈 Change year as needed