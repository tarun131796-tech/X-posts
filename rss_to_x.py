import feedparser
import tweepy
import time
import random
import os
import logging

# ================== LOGGING ==================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================

RSS_FEEDS = [
    "https://news.google.com/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
]

POSTS_PER_DAY = 10
DELAY_RANGE = (120, 300)  # 2–5 minutes between posts

# ================== X CREDENTIALS ==================

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# ================== X AUTH ==================

def get_api():
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        logger.warning("X credentials not found. Running in DRY-RUN mode.")
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
        logger.info("Authenticated with X successfully.")
        return api
    except Exception as e:
        logger.error(f"X authentication failed: {e}")
        return None

# ================== FETCH RSS ==================

def get_news_items():
    items = []

    for feed_url in RSS_FEEDS:
        logger.info(f"Fetching feed: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed issue detected: {feed.bozo_exception}")

            feed_title = (
                feed.feed.title
                if hasattr(feed, "feed") and hasattr(feed.feed, "title")
                else "Unknown Source"
            )

            for entry in getattr(feed, "entries", []):
                if hasattr(entry, "title") and hasattr(entry, "link"):
                    items.append({
                        "title": entry.title.strip(),
                        "link": entry.link.strip(),
                        "source": feed_title
                    })

        except Exception as e:
            logger.error(f"Error processing feed {feed_url}: {e}")

    random.shuffle(items)
    selected = items[:POSTS_PER_DAY]

    logger.info(f"Selected {len(selected)} news items.")
    return selected

# ================== POST ==================

def post_to_x(api, item):
    text = (
        f"📰 {item['title']}\n\n"
        f"Source: {item['source']}\n"
        f"{item['link']}"
    )

    text = text[:280]

    if api:
        try:
            api.update_status(status=text)
            logger.info(f"Posted: {item['title']}")
        except Exception as e:
            logger.error(f"Failed to post '{item['title']}': {e}")
    else:
        safe_text = text.replace("\n", " ")
        logger.info(f"[DRY RUN] Would post: {safe_text}")

# ================== MAIN ==================

def run():
    logger.info("RSS-to-X bot started.")
    api = get_api()
    news = get_news_items()

    if not news:
        logger.warning("No news items found. Exiting.")
        return

    for index, item in enumerate(news, start=1):
        logger.info(f"Processing post {index}/{len(news)}")
        post_to_x(api, item)

        if api and index < len(news):
            delay = random.randint(*DELAY_RANGE)
            logger.info(f"Sleeping for {delay} seconds.")
            time.sleep(delay)

    logger.info("RSS-to-X bot finished successfully.")

# ================== ENTRY ==================

if __name__ == "__main__":
    run()
