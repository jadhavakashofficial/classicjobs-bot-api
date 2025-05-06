import requests
from requests.auth import HTTPBasicAuth
from utils.load_env import WORDPRESS_SITE, WORDPRESS_USER, WORDPRESS_APP_PASSWORD

def get_all_job_titles():
    titles = []
    page = 1
    while True:
        url = f"{WORDPRESS_SITE}/wp-json/wp/v2/posts"
        res = requests.get(
            url,
            params={"per_page": 100, "page": page},
            auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD)
        )
        if res.status_code != 200:
            break
        posts = res.json()
        if not posts:
            break
        for post in posts:
            titles.append(post["title"]["rendered"])
        page += 1
    return titles

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