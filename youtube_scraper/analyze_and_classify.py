import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
from utils.load_env import OPENAI_API_KEY
from youtube_scraper.fetch_latest_videos import fetch_all_latest_videos


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])
        full_text = " ".join([entry["text"] for entry in transcript])
        return full_text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

def classify_transcript(text):
    prompt = f"""
    Categorize the following YouTube video transcript into one of these:
    - job_update
    - exam_strategy
    - interview_tips
    - career_faq

    Transcript:
    {text[:3000]}

    Return only the category name.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()

# Main process
if __name__ == "__main__":
    videos = fetch_all_latest_videos()
    for video in videos:
        print(f"\n🎥 {video['title']} → https://youtube.com/watch?v={video['video_id']}")
        transcript = get_transcript(video["video_id"])

        if transcript:
            print("📄 Transcript found.")
            category = classify_transcript(transcript)
            print(f"📌 Category: {category}")
        else:
            print("❌ No transcript available.")
