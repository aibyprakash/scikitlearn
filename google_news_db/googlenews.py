from gnews import GNews
from newspaper import Article
from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime, Boolean
from datetime import datetime
import time
import hashlib
import os

def load_stock_names(filename):
    """Load stock names and symbols from a text file."""
    stocks = set()  # Using set to automatically avoid duplicates
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    # Split by tab or comma or space
                    parts = [p.strip() for p in line.replace(',', ' ').split() if p.strip()]
                    stocks.update(parts)  # Add all parts to the set
    return sorted(stocks)  # Return as sorted list

def generate_article_id(url):
    """Generate a unique ID for each news article based on its URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

# Initialize Google News client
news = GNews(
    language='en',
    country='US',
    max_results=20,  # Increased from 10 to get more coverage
    period='7d'  # Only get recent news
)

# Load stock names from file
stock_names = load_stock_names('stock_names.txt')
if not stock_names:
    stock_names = ["CRUDE OIL", "NSE", "NATURAL GAS", "CME", "CRUDE", "CL", "NG"]
    print("Warning: Using default stock names as stock_names.txt was empty or not found")

print(f"Tracking news for {len(stock_names)} stocks/symbols: {', '.join(stock_names[:10])}...")

# Database setup with improved schema
engine = create_engine('sqlite:///financial_news.db')
metadata = MetaData()

news_table = Table('financial_news', metadata,
    Column('id', String(32), primary_key=True),
    Column('datetime', DateTime, index=True),
    Column('stock_name', String(50), index=True),
    Column('title', String(500)),
    Column('url', String(500), unique=True),
    Column('author', String(100)),
    Column('content', String),
    Column('source', String(100)),
    Column('processed', Boolean, default=False),
    Column('created_at', DateTime, default=datetime.now)
)

metadata.create_all(engine)

def article_exists(conn, article_id):
    """Check if article already exists in database."""
    return conn.execute(
        news_table.select().where(news_table.c.id == article_id)
    ).fetchone() is not None

def save_article(conn, article_data):
    """Save article to database if it doesn't exist."""
    try:
        conn.execute(news_table.insert().values(article_data))
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

# Main processing loop
with engine.connect() as conn:
    for stock in stock_names:
        print(f"\nFetching news for: {stock}")
        try:
            articles = news.get_news(stock)
            if not articles:
                print(f"No articles found for {stock}")
                continue

            for item in articles:
                try:
                    article_id = generate_article_id(item['url'])
                    
                    if article_exists(conn, article_id):
                        continue  # Skip duplicates

                    # Download and parse article
                    article = Article(item['url'])
                    article.download()
                    article.parse()

                    # Prepare data for insertion
                    article_data = {
                        'id': article_id,
                        'datetime': datetime.strptime(item['published date'], '%a, %d %b %Y %H:%M:%S %Z'),
                        'stock_name': stock,
                        'title': item['title'],
                        'url': item['url'],
                        'author': article.authors[0] if article.authors else 'Unknown',
                        'content': article.text,
                        'source': item['publisher']['title'] if 'publisher' in item else None,
                        'processed': False
                    }

                    if save_article(conn, article_data):
                        print(f"✓ Saved: {item['title'][:60]}...")
                    else:
                        print(f"✗ Failed to save: {item['title'][:60]}...")

                    time.sleep(1)  # Respectful delay between requests

                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching news for {stock}: {e}")
            continue

print("\nNews collection complete!")
