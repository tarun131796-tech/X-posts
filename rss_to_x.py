import feedparser
import tweepy
import time
import random

# -------- CONFIG --------

RSS_FEEDS = [
    "https://news.google.com/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.reuters.com/reuters/topNews"
]

POSTS_PER_DAY = 10
DELAY_RANGE = (120, 300)  # 2–5 minutes between posts

# X credentials (use env vars in deployment)
X_API_KEY = "YOUR_X_API_KEY"
X_API_SECRET = "YOUR_X_API_SECRET"
X_ACCESS_TOKEN = "YOUR_X_ACCESS_TOKEN"
X_ACCESS_SECRET = "YOUR_X_ACCESS_SECRET"

# -------- X AUTH --------

auth = tweepy.OAuth1UserHandler(
    X_API_KEY,
    X_API_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_SECRET
)
api = tweepy.API(auth)

# -------- FETCH RSS --------

def get_news_items():
    items = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": feed.feed.title
            })

    random.shuffle(items)
    return items[:POSTS_PER_DAY]

# -------- POST --------

def post_to_x(item):
    text = (
        f"📰 {item['title']}\n\n"
        f"Source: {item['source']}\n"
        f"{item['link']}"
    )
    api.update_status(status=text[:280])

# -------- MAIN --------

def run():
    news = get_news_items()

    for item in news:
        post_to_x(item)
        time.sleep(random.randint(*DELAY_RANGE))

if __name__ == "__main__":
    run()
