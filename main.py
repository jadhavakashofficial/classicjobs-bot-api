import os
from youtube_scraper.fetch_latest_videos import fetch_all_latest_videos
from youtube_scraper.analyze_videos import get_transcript, classify_transcript
from youtube_scraper.fetch_comments import fetch_comments
from competitor_scraper.fetch_jobs_from_apis import fetch_jobs_from_all_apis
from wordpress_draft_creator.create_drafts import create_wordpress_draft

def log_for_bot_training(video, transcript, comments):
    folder = "bot_training_logs"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/{video['video_id']}.txt", "w", encoding="utf-8") as f:
        f.write(f"# Title: {video['title']}\n")
        f.write(f"# YouTube Link: https://youtube.com/watch?v={video['video_id']}\n\n")
        f.write("## Transcript:\n")
        f.write(transcript or "Transcript not available\n")
        f.write("\n\n## Comments:\n")
        for c in comments:
            f.write(f"- {c}\n")

def run_daily_pipeline():
    print("🚀 Starting Daily Pipeline...\n")

    # 1. Fetch videos
    videos = fetch_all_latest_videos()

    # 2. Fetch jobs (to post on your site)
    jobs = fetch_jobs_from_all_apis()
    print(f"\n📝 Drafting {len(jobs)} job posts to classicjobs.in...\n")
    for job in jobs:
        create_wordpress_draft(job["title"], job["link"])

    # 3. Process each video
    for video in videos:
        print(f"\n🎥 {video['title']}")
        print(f"🔗 https://youtube.com/watch?v={video['video_id']}")

        transcript = get_transcript(video["video_id"])
        if transcript:
            category = classify_transcript(transcript)
            print(f"📌 Category: {category}")
        else:
            print("❌ Transcript not available.")
            category = "unknown"

        # Fetch top comments
        comments = fetch_comments(video["video_id"])
        print(f"🗨️ Comments fetched: {len(comments)}")

        # Log for bot training (title, transcript, comments)
        log_for_bot_training(video, transcript, comments)

    print("\n✅ Daily run complete. Data logged for bot training.\n")

if __name__ == "__main__":
    run_daily_pipeline()
