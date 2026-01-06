import feedparser
import tweepy
import time
import random
import os
import logging

# -------- LOGGING --------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -------- CONFIG --------

RSS_FEEDS = [
    "https://news.google.com/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    # "https://feeds.reuters.com/reuters/topNews" # Removed broken feed
]

POSTS_PER_DAY = 10
DELAY_RANGE = (120, 300)  # 2–5 minutes between posts

# X credentials (use env vars in deployment)
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

# -------- X AUTH --------

def get_api():
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        logger.warning("X credentials not found in environment variables. Running in dry-run mode (no posting).")
        return None

    try:
        auth = tweepy.OAuth1UserHandler(
            X_API_KEY,
            X_API_SECRET,
            X_ACCESS_TOKEN,
            X_ACCESS_SECRET
        )
        api = tweepy.API(auth)
        api.verify_credentials()
        return api
    except Exception as e:
        logger.error(f"Error authenticating with X: {e}")
        return None

# -------- FETCH RSS --------

def get_news_items():
    items = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logger.warning(f"Potential issue with feed {feed_url}: {feed.bozo_exception}")

            if not hasattr(feed, 'entries'):
                logger.warning(f"No entries found in feed {feed_url}")
                continue

            feed_title = feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else "Unknown Source"

            for entry in feed.entries:
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": feed_title
                })
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")

    random.shuffle(items)
    return items[:POSTS_PER_DAY]

# -------- POST --------

def post_to_x(api, item):
    text = (
        f"📰 {item['title']}\n\n"
        f"Source: {item['source']}\n"
        f"{item['link']}"
    )

    if api:
        try:
            api.update_status(status=text[:280])
            logger.info(f"Posted: {item['title']}")
        except Exception as e:
            logger.error(f"Failed to post item {item['title']}: {e}")
    else:
        logger.info(f"[DRY RUN] Would post: {text[:280].replace('\n', ' ')}")

# -------- MAIN --------

def run():
    api = get_api()
    news = get_news_items()

    if not news:
        logger.info("No news items found.")
        return

    for item in news:
        post_to_x(api, item)
        # Only sleep if we are actually posting or simulating a real run
        if api:
             time.sleep(random.randint(*DELAY_RANGE))

if __name__ == "__main__":
    run()
