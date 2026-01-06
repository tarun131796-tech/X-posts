"""
X Monetization Bot - Automated + Human Value System
Uses FREE Gemini 2.5 Flash for AI-generated insights
"""

import os
import time
import random
import requests
import tweepy
import json
from datetime import datetime
from typing import List, Dict

# ============================================================================
# CONFIGURATION - Customize for your niche
# ============================================================================

NICHE_CONFIG = {
    'ai_tech': {
        'keywords': ['artificial intelligence', 'AI', 'machine learning', 'ChatGPT', 'tech startup'],
        'hashtags': ['#AI', '#TechNews', '#MachineLearning', '#Innovation'],
        'affiliate_links': {
            'jasper': 'https://jasper.ai?via=YOUR_CODE',
            'notion': 'https://notion.so?via=YOUR_CODE'
        }
    },
    'crypto': {
        'keywords': ['cryptocurrency', 'bitcoin', 'ethereum', 'blockchain', 'DeFi'],
        'hashtags': ['#Crypto', '#Bitcoin', '#Web3', '#Blockchain'],
        'affiliate_links': {
            'coinbase': 'https://coinbase.com/join/YOUR_CODE',
            'binance': 'https://binance.com/ref/YOUR_CODE'
        }
    },
    'finance': {
        'keywords': ['stock market', 'investing', 'trading', 'stocks', 'finance'],
        'hashtags': ['#StockMarket', '#Investing', '#Finance', '#Trading'],
        'affiliate_links': {
            'webull': 'https://webull.com/ref/YOUR_CODE',
            'tradingview': 'https://tradingview.com?via=YOUR_CODE'
        }
    },
    'side_hustle': {
        'keywords': ['side hustle', 'make money online', 'passive income', 'entrepreneur', 'startup'],
        'hashtags': ['#SideHustle', '#Entrepreneur', '#PassiveIncome', '#MakeMoneyOnline'],
        'affiliate_links': {
            'shopify': 'https://shopify.com/ref/YOUR_CODE',
            'canva': 'https://canva.com/ref/YOUR_CODE'
        }
    }
}

# Select your niche here
SELECTED_NICHE = 'ai_tech'  # Change to 'crypto', 'finance', or 'side_hustle' as needed
NICHE = NICHE_CONFIG[SELECTED_NICHE]

# ============================================================================
# API SETUP
# ============================================================================

# X/Twitter API
client = tweepy.Client(
    bearer_token=os.getenv('X_BEARER_TOKEN'),
    consumer_key=os.getenv('X_API_KEY'),
    consumer_secret=os.getenv('X_API_SECRET'),
    access_token=os.getenv('X_ACCESS_TOKEN'),
    access_token_secret=os.getenv('X_ACCESS_SECRET')
)

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ============================================================================
# CONTENT GENERATION WITH GEMINI 2.5 FLASH (FREE!)
# ============================================================================

def generate_insight_with_gemini(headline: str, description: str = "") -> str:
    """
    Use FREE Gemini 2.5 Flash to generate valuable insights from news
    This makes your posts unique and valuable vs just sharing links
    """
    prompt = f"""You are a {SELECTED_NICHE} expert on X/Twitter with a growing audience.
    
News Headline: {headline}
Description: {description}

Write a compelling 2-sentence insight about this news that:
1. Provides a unique angle or hot take
2. Is slightly contrarian or thought-provoking
3. Makes people want to engage
4. Shows expertise
5. Stays under 150 characters total

Do not use hashtags. Be direct and punchy."""

    try:
        # Gemini 2.5 Flash API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-exp:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 150,
                "topP": 0.95
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            insight = data['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean up any extra formatting
            insight = insight.replace('"', '').replace('*', '').strip()
            return insight[:150]  # Ensure under limit
        else:
            print(f"Gemini API error: {response.status_code}")
            # Fallback if API fails
            return f"Breaking: {headline[:100]}"
            
    except Exception as e:
        print(f"AI generation error: {e}")
        return f"Interesting development in {SELECTED_NICHE}."

# ============================================================================
# NEWS FETCHING WITH NICHE FOCUS
# ============================================================================

def fetch_niche_news(num_articles: int = 10) -> List[Dict]:
    """Fetch news relevant to your niche"""
    
    # Build query from niche keywords
    query = ' OR '.join(NICHE['keywords'][:3])  # Top 3 keywords
    
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            
            # Filter and clean
            filtered = []
            for article in articles[:num_articles * 2]:  # Get extra to filter
                if article.get('title') and article.get('url'):
                    if '[Removed]' not in article.get('title', ''):
                        filtered.append({
                            'title': article['title'],
                            'description': article.get('description', ''),
                            'url': article['url'],
                            'source': article.get('source', {}).get('name', 'Unknown')
                        })
                        
            return filtered[:num_articles]
        else:
            print(f"NewsAPI error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ============================================================================
# DUPLICATE PREVENTION
# ============================================================================

def load_posted_urls():
    """Load previously posted URLs to avoid duplicates"""
    try:
        with open("posted_news.log", "r") as f:
            urls = set()
            for line in f:
                if " | " in line:
                    # Extract URL from log line
                    parts = line.split(" | ")
                    if len(parts) >= 3:
                        tweet_text = parts[2]
                        # Extract URL from tweet text
                        if "http" in tweet_text:
                            url_start = tweet_text.find("http")
                            url_end = tweet_text.find(" ", url_start)
                            if url_end == -1:
                                url_end = len(tweet_text)
                            urls.add(tweet_text[url_start:url_end].strip())
            return urls
    except FileNotFoundError:
        return set()

def is_duplicate(article_url: str, posted_urls: set) -> bool:
    """Check if article was already posted"""
    return article_url in posted_urls

# ============================================================================
# SMART TWEET CREATION
# ============================================================================

def create_value_tweet(article: Dict, index: int, add_affiliate: bool = False) -> str:
    """Create a tweet that provides value beyond just sharing a link"""
    
    # Generate AI insight using Gemini
    insight = generate_insight_with_gemini(article['title'], article['description'])
    
    # Add variety to format
    formats = [
        # Format 1: Insight + Link
        f"{insight}\n\n🔗 {article['url']}",
        
        # Format 2: Question hook + Link  
        f"{insight}\n\nFull story: {article['url']}",
        
        # Format 3: Numbered with context
        f"#{index} {insight}\n\nRead more: {article['url']}"
    ]
    
    base_tweet = random.choice(formats)
    
    # Add hashtags (max 2)
    selected_hashtags = random.sample(NICHE['hashtags'], min(2, len(NICHE['hashtags'])))
    base_tweet += '\n\n' + ' '.join(selected_hashtags)
    
    # Occasionally add affiliate link (20% of posts)
    if add_affiliate and random.random() < 0.2 and NICHE['affiliate_links']:
        affiliate_name, affiliate_url = random.choice(list(NICHE['affiliate_links'].items()))
        base_tweet += f"\n\n💡 Tool I use: {affiliate_url}"
    
    # Ensure under 280 chars
    if len(base_tweet) > 280:
        # Trim the insight if needed
        excess = len(base_tweet) - 280
        insight_trimmed = insight[:len(insight) - excess - 3] + "..."
        base_tweet = base_tweet.replace(insight, insight_trimmed)
    
    return base_tweet[:280]

# ============================================================================
# ENGAGEMENT TRACKING
# ============================================================================

def track_post_performance(tweet_id: str, tweet_text: str):
    """Log posts for performance tracking"""
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'tweet_id': tweet_id,
        'text': tweet_text[:100],
        'niche': SELECTED_NICHE
    }
    
    # Append to JSON log file
    log_file = 'post_analytics.json'
    
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Also append to simple text log
    with open("posted_news.log", "a") as f:
        f.write(f"{datetime.now()} | ID: {tweet_id} | {tweet_text}\n")

# ============================================================================
# POSTING LOGIC
# ============================================================================

def post_tweet(text: str) -> str:
    """Post tweet and return ID"""
    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data['id']
        print(f"✅ Posted: {text[:80]}...")
        return tweet_id
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return None

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main posting routine"""
    
    print(f"🚀 Starting X Monetization Bot for {SELECTED_NICHE.upper()}")
    print(f"🤖 Using Gemini 2.5 Flash (FREE) for AI insights")
    print(f"Target: 10 posts with unique value-added content\n")
    
    # Load previously posted URLs
    posted_urls = load_posted_urls()
    print(f"📝 Loaded {len(posted_urls)} previously posted URLs")
    
    # Fetch niche-specific news
    articles = fetch_niche_news(15)  # Get extra for filtering
    
    if not articles:
        print("❌ No articles fetched. Exiting.")
        return
    
    print(f"📰 Fetched {len(articles)} articles\n")
    
    # Filter out duplicates
    fresh_articles = [a for a in articles if not is_duplicate(a['url'], posted_urls)]
    print(f"✨ {len(fresh_articles)} new articles after duplicate removal\n")
    
    if len(fresh_articles) < 10:
        print(f"⚠️  Warning: Only {len(fresh_articles)} fresh articles available")
    
    # Take up to 10 articles
    articles_to_post = fresh_articles[:10]
    
    # Post with smart spacing
    delays_minutes = [random.randint(30, 90) for _ in range(len(articles_to_post) - 1)]
    
    posted_count = 0
    
    for i, article in enumerate(articles_to_post):
        # Create value-added tweet
        add_affiliate = (i % 5 == 0)  # Every 5th post includes affiliate
        tweet_text = create_value_tweet(article, i + 1, add_affiliate)
        
        # Post
        tweet_id = post_tweet(tweet_text)
        
        if tweet_id:
            track_post_performance(tweet_id, tweet_text)
            posted_count += 1
            
            # Wait before next post (except for last one)
            if i < len(articles_to_post) - 1:
                wait_time = delays_minutes[i]
                print(f"⏳ Waiting {wait_time} minutes before next post...\n")
                time.sleep(wait_time * 60)
        else:
            print(f"⚠️  Skipping article due to posting error")
    
    print(f"\n✅ Session complete! Posted {posted_count}/{len(articles_to_post)} tweets")
    print(f"📊 Check post_analytics.json for performance tracking")

# ============================================================================
# BONUS: ENGAGEMENT AUTOMATION
# ============================================================================

def auto_engage():
    """
    Bonus function: Auto-engage with mentions/replies
    Run this separately or add to workflow
    """
    try:
        # Get recent mentions
        me = client.get_me()
        mentions = client.get_users_mentions(
            id=me.data.id,
            max_results=10
        )
        
        if not mentions.data:
            print("No new mentions")
            return
        
        for mention in mentions.data:
            # Generate contextual reply using Gemini
            reply_prompt = f"Someone tweeted: '{mention.text}'. Write a helpful, friendly 1-sentence reply as a {SELECTED_NICHE} expert. Keep it under 200 characters."
            
            reply = generate_insight_with_gemini(mention.text, reply_prompt)
            
            # Post reply
            client.create_tweet(
                text=reply[:280],
                in_reply_to_tweet_id=mention.id
            )
            
            print(f"✅ Replied to mention")
            time.sleep(60)  # Rate limit protection
            
    except Exception as e:
        print(f"Engagement error: {e}")

if __name__ == "__main__":
    main()
    
    # Optionally run engagement
    # auto_engage()
