import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bot_api')))

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_scraper.fetch_comments import fetch_comments
from youtube_scraper.fetch_videos_by_year import fetch_videos_by_year

os.makedirs("bot_training_logs", exist_ok=True)

def clean_text(text):
    return text.replace('\n', ' ').strip()

def collect_2021_data():
    print("📥 Collecting all videos from 2021...")
    videos = fetch_videos_by_year(2021)
    combined_lines = []

    for video in videos:
        video_id = video["video_id"]
        title = video["title"]
        print("🎥", title)

        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
            transcript = clean_text(" ".join([t["text"] for t in transcript_data]))
            comments = fetch_comments(video_id)
            combined_lines.append(
                f"=== {title} ===\n\n"
                f"Transcript:\n{transcript}\n\nTop Comments:\n" + "\n".join(comments) + "\n\n"
            )
        except Exception as e:
            print(f"❌ Skipped {title}: {e}")

    path = "bot_training_logs/2021_combined.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))

    print(f"✅ Saved combined data for 2021 → {path}")

if __name__ == "__main__":
    collect_2021_data()