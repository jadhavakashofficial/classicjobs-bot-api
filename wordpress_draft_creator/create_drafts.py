import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from requests.auth import HTTPBasicAuth
from utils.load_env import WORDPRESS_SITE, WORDPRESS_USER, WORDPRESS_APP_PASSWORD
from competitor_scraper.fetch_jobs_from_apis import fetch_jobs_from_all_apis

# ✅ Fetch all existing post titles (drafts + published)
def fetch_existing_titles():
    existing_titles = set()
    page = 1

    while True:
        endpoint = f"{WORDPRESS_SITE}/wp-json/wp/v2/posts"
        response = requests.get(
            endpoint,
            params={"per_page": 100, "page": page},
            auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD)
        )

        if response.status_code != 200:
            print(f"⚠️ Failed to fetch existing posts: {response.status_code}")
            break

        posts = response.json()
        if not posts:
            break

        for post in posts:
            existing_titles.add(post.get("title", {}).get("rendered", "").strip().lower())

        page += 1

    return existing_titles

# ✅ Create a single post
def create_wordpress_draft(title, source_url, existing_titles):
    if title.strip().lower() in existing_titles:
        print(f"⏭️ Skipped (duplicate): {title}")
        return

    endpoint = f"{WORDPRESS_SITE}/wp-json/wp/v2/posts"
    post_data = {
        "title": title,
        "content": f"<p>Source: <a href='{source_url}' target='_blank'>{source_url}</a></p>",
        "status": "draft"
    }

    response = requests.post(
        endpoint,
        json=post_data,
        auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD)
    )

    if response.status_code == 201:
        print(f"✅ Draft created: {title}")
    else:
        print(f"❌ Failed to create draft: {title} — {response.status_code}")
        print(response.text)

# ✅ Wrapper function for external import
def create_wordpress_drafts(jobs):
    existing_titles = fetch_existing_titles()
    for job in jobs:
        create_wordpress_draft(job["title"], job["link"], existing_titles)

# ✅ CLI usage
if __name__ == "__main__":
    jobs = fetch_jobs_from_all_apis()
    create_wordpress_drafts(jobs)
