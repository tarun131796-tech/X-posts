# RSS to X (Twitter) Bot

This is a Python script that fetches news from various RSS feeds (Google News, BBC, Reuters) and automatically posts selected items to an X (formerly Twitter) account.

## Features

- Fetches news from multiple RSS sources.
- Randomly selects a configurable number of items to post each run.
- Posts news title, source, and link to X.
- Includes a random delay between posts to mimic human behavior.

## Prerequisites

- Python 3.x
- An X (Twitter) Developer account with API access.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Open `rss_to_x.py` and configure the following variables:

### API Keys
Replace the placeholder strings with your actual X API credentials:

```python
X_API_KEY = "YOUR_X_API_KEY"
X_API_SECRET = "YOUR_X_API_SECRET"
X_ACCESS_TOKEN = "YOUR_X_ACCESS_TOKEN"
X_ACCESS_SECRET = "YOUR_X_ACCESS_SECRET"
```

> **Note:** For a production deployment, it is recommended to use environment variables instead of hardcoding credentials in the script.

### Settings
You can adjust the behavior by modifying these constants:

- `RSS_FEEDS`: Add or remove RSS feed URLs.
- `POSTS_PER_DAY`: Number of posts to make per run (default: 10).
- `DELAY_RANGE`: Tuple representing the minimum and maximum seconds to wait between posts (default: 120-300 seconds).

## Usage

Run the script using Python:

```bash
python rss_to_x.py
```

The script will fetch news items, shuffle them, select a subset, and post them one by one with a delay.

## Dependencies

- `feedparser`: To parse RSS feeds.
- `tweepy`: To interact with the X API.
- `requests`: (Included in requirements, utilized by dependencies).
