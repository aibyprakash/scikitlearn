from gnews import GNews
from newspaper import Article
from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime, Boolean
from datetime import datetime, timedelta
import time
import hashlib
import os
from typing import List, Dict, Set

def clear_console():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_stock_names(filename: str) -> List[str]:
    """Load and clean stock names from text file"""
    stocks: Set[str] = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.split('#')[0].strip()  # Remove comments
                if line:
                    # Split by any whitespace or comma
                    stocks.update(part.strip().upper() for part in line.replace(',', ' ').split())
    return sorted(stocks)

def generate_article_id(url: str) -> str:
    """Create consistent hash ID from URL"""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

class NewsMonitor:
    def __init__(self):
        self.news_client = GNews(
            language='en',
            country='US',
            max_results=25,
            period='1d',  # Only last day's news
            exclude_websites=["twitter.com", "facebook.com"]
        )
        self.engine = create_engine('sqlite:///financial_news.db?cache_size=5000')
        self.setup_database()
        self.stock_names = self.load_assets()

    def setup_database(self):
        """Initialize database schema"""
        metadata = MetaData()
        Table('financial_news', metadata,
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
        metadata.create_all(self.engine)

    def load_assets(self) -> List[str]:
        """Load assets with fallback to defaults"""
        stocks = load_stock_names('stock_names.txt')
        if not stocks:
            stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", 
                     "CRUDE OIL", "NATURAL GAS", "CL", "NG"]
            print("⚠️ Using default stocks - check stock_names.txt")
        return stocks

    def run_cycle(self) -> int:
        """Complete one collection cycle, return new articles count"""
        new_articles = 0
        with self.engine.connect() as conn:
            for stock in self.stock_names:
                try:
                    articles = self.news_client.get_news(stock)
                    if not articles:
                        continue

                    for item in articles:
                        article_id = generate_article_id(item['url'])
                        
                        # Skip duplicates
                        if conn.execute(
                            "SELECT 1 FROM financial_news WHERE id = ?", 
                            (article_id,)
                        ).fetchone():
                            continue

                        # Process article
                        article = Article(item['url'])
                        article.download()
                        article.parse()

                        conn.execute(
                            """INSERT INTO financial_news 
                            (id, datetime, stock_name, title, url, 
                             author, content, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                article_id,
                                datetime.strptime(
                                    item['published date'], 
                                    '%a, %d %b %Y %H:%M:%S %Z'
                                ),
                                stock,
                                item['title'],
                                item['url'],
                                ', '.join(article.authors) if article.authors else 'Unknown',
                                article.text,
                                item.get('publisher', {}).get('title')
                            )
                        )
                        new_articles += 1
                        print(f"✅ [{stock}] {item['title'][:70]}...")

                        time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"⚠️ Error on {stock}: {str(e)}")
                    continue

        return new_articles

    def continuous_monitor(self):
        """Run continuous monitoring with 15-minute cycles"""
        cycle_count = 0
        while True:
            cycle_count += 1
            cycle_start = datetime.now()
            clear_console()

            print(f"📈 News Monitor - Cycle {cycle_count}")
            print(f"🔍 Tracking {len(self.stock_names)} assets")
            print("⏳ Running collection...\n")

            new_articles = self.run_cycle()
            print(f"\n🎯 Cycle complete: Added {new_articles} new articles")

            # Calculate time until next cycle
            elapsed = (datetime.now() - cycle_start).total_seconds()
            sleep_time = max(900 - elapsed, 0)  # 15 minute cycles

            if sleep_time > 0:
                mins, secs = divmod(int(sleep_time), 60)
                print(f"\n⏱ Next cycle in {mins:02d}:{secs:02d}")
                time.sleep(sleep_time)

if __name__ == "__main__":
    monitor = NewsMonitor()
    try:
        monitor.continuous_monitor()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n💥 Critical error: {str(e)}")
