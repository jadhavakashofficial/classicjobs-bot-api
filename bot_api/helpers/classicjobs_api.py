import requests
from utils.load_env import WORDPRESS_SITE

def search_classicjobs_posts(query):
    try:
        url = f"{WORDPRESS_SITE}/wp-json/wp/v2/posts"
        params = {"search": query, "per_page": 1}
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            post = response.json()[0]
            return post["title"]["rendered"], post["link"]
    except Exception as e:
        print("❌ Error fetching ClassicJobs post:", e)
    return None, None
