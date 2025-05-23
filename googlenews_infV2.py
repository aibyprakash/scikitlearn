from gnews import GNews
from newspaper import Article
from sqlalchemy import create_engine, Table, Column, String, MetaData, DateTime, Boolean
from datetime import datetime
import time
import hashlib
import os
import threading
from typing import List, Set

class LiveClock:
    def __init__(self):
        self.running = True
        self.clock_thread = threading.Thread(target=self._run_clock)
        
    def _run_clock(self):
        while self.running:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"🕒 {current_time}", end='\r', flush=True)
            time.sleep(1)
    
    def start(self):
        self.clock_thread.start()
    
    def stop(self):
        self.running = False
        self.clock_thread.join()
        print(" " * 15, end='\r')  # Clear clock display

def clear_console():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_stock_names(filename: str) -> List[str]:
    """Load and clean stock names from text file"""
    stocks: Set[str] = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.split('#')[0].strip()
                if line:
                    stocks.update(part.strip().upper() for part in line.replace(',', ' ').split())
    return sorted(stocks)

def generate_article_id(url: str) -> str:
    """Create consistent hash ID from URL"""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

class NewsMonitor:
    def __init__(self):
        self.clock = LiveClock()
        self.news_client = GNews(
            language='en',
            country='US',
            max_results=25,
            period='1d',
            exclude_websites=["twitter.com", "facebook.com"]
        )
        self.engine = create_engine('sqlite:///financial_news.db?cache_size=5000')
        self.setup_database()
        self.stock_names = load_stock_names('stock_names.txt') or [
            "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
            "CRUDE OIL", "NATURAL GAS", "CL", "NG"
        ]

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

    def run_collection(self) -> int:
        """Run one complete collection cycle"""
        new_articles = 0
        with self.engine.connect() as conn:
            for stock in self.stock_names:
                try:
                    articles = self.news_client.get_news(stock)
                    if not articles:
                        continue

                    for item in articles:
                        article_id = generate_article_id(item['url'])
                        
                        if conn.execute(
                            "SELECT 1 FROM financial_news WHERE id = ?", 
                            (article_id,)
                        ).fetchone():
                            continue

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
                        print(f"\n📰 {stock}: {item['title'][:60]}...")

                        time.sleep(1)

                except Exception as e:
                    print(f"\n⚠️ Error on {stock}: {str(e)}")
                    continue

        return new_articles

    def show_countdown(self, seconds: int):
        """Display animated countdown timer with live clock"""
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            print(f"⏳ Next scan in {mins:02d}:{secs:02d}", end=' ', flush=True)
            time.sleep(1)
            seconds -= 1
        print("\r" + " " * 40, end='\r')  # Clear line

    def start_monitoring(self):
        """Start continuous monitoring with live clock"""
        try:
            self.clock.start()
            clear_console()
            print(f"📈 Tracking {len(self.stock_names)} assets | Live News Monitor")
            
            while True:
                print("\n🔍 Scanning for news updates...")
                new_count = self.run_collection()
                print(f"\n✅ Added {new_count} new articles")
                
                # Wait for next cycle with countdown
                self.show_countdown(900)  # 15 minutes

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n💥 Critical error: {str(e)}")
        finally:
            self.clock.stop()

if __name__ == "__main__":
    monitor = NewsMonitor()
    monitor.start_monitoring()
