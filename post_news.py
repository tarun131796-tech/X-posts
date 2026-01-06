import os
import time
import random
import requests
import tweepy
import datetime
import git  # For committing log back to repo (requires gitpython)

# Load credentials from environment (GitHub secrets)
client = tweepy.Client(
    bearer_token=os.getenv('X_BEARER_TOKEN'),
    consumer_key=os.getenv('X_API_KEY'),
    consumer_secret=os.getenv('X_API_SECRET'),
    access_token=os.getenv('X_ACCESS_TOKEN'),
    access_token_secret=os.getenv('X_ACCESS_SECRET')
)

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

def fetch_top_news():
    response = requests.get(NEWS_URL)
    if response.status_code != 200:
        print("Error fetching news")
        return []
    articles = response.json().get('articles', [])[:10]
    return [article['title'] + " " + (article['url'] or "") for article in articles]

def post_tweet(text):
    try:
        response = client.create_tweet(text=text[:280])  # Truncate if needed
        print(f"Posted: {text[:100]}...")
        return response.data['id']
    except Exception as e:
        print(f"Error posting: {e}")
        return None

def log_post(tweet_id, text):
    log_file = "posted_news.log"
    with open(log_file, "a") as f:
        f.write(f"{datetime.datetime.now()} | ID: {tweet_id} | {text}\n")

def commit_log():
    try:
        repo = git.Repo('.')
        repo.index.add(['posted_news.log'])
        repo.index.commit("Update news log")
        origin = repo.remote('origin')
        origin.push()
        print("Log committed and pushed")
    except Exception as e:
        print(f"Git commit error: {e}")

if __name__ == "__main__":
    news_items = fetch_top_news()
    if not news_items:
        print("No news fetched")
        exit()

    print(f"Fetched {len(news_items)} news items")

    delays = [random.randint(30, 120) for _ in range(9)]  # Random delays in minutes between posts

    for i, item in enumerate(news_items):
        tweet_text = f"Trending News #{i+1}: {item} #News #Trending"
        tweet_id = post_tweet(tweet_text)
        if tweet_id:
            log_post(tweet_id, tweet_text)

        if i < len(news_items) - 1:  # Wait before next post
            wait_minutes = delays[i]
            print(f"Waiting {wait_minutes} minutes before next post...")
            time.sleep(wait_minutes * 60)

    commit_log()  # Save log to GitHub
