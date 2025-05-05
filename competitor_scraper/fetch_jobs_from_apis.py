import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.load_env import COMPETITOR_JOB_APIS
from bs4 import BeautifulSoup

def clean_html(raw_html):
    """Removes HTML tags from job content."""
    return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ", strip=True)

def fetch_jobs_from_all_apis():
    all_jobs = []

    for api_url in COMPETITOR_JOB_APIS:
        if not api_url:
            continue

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json, text/plain, */*",
                "Referer": api_url
            }

            response = requests.get(api_url.strip(), headers=headers, timeout=10)
            if response.status_code == 200:
                posts = response.json()
                for post in posts[:2]:  # Get top 2 per site
                    title = post.get("title", {}).get("rendered", "No Title")
                    link = post.get("link", "No Link")
                    content_raw = post.get("content", {}).get("rendered", "")
                    content = clean_html(content_raw)
                    all_jobs.append({
                        "title": title,
                        "link": link,
                        "content": content
                    })
            else:
                print(f"❌ Failed to fetch from {api_url} — Status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error fetching from {api_url} — {e}")

    return all_jobs

# Optional test run
if __name__ == "__main__":
    jobs = fetch_jobs_from_all_apis()
    for job in jobs:
        print(f"\n{job['title']}")
        print(f"🔗 {job['link']}")
        print(f"📝 {job['content'][:200]}...")  # Preview 200 chars
