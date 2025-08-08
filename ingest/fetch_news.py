"""News article ingestion from News API"""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NEWS_API_KEY, NEWS_SOURCES, MAX_ARTICLES_PER_BATCH
from database import StoryGenomeDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsIngester:
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.db = StoryGenomeDB()
        
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
    
    def fetch_articles(self, query: str = None, sources: List[str] = None, 
                      from_date: datetime = None, to_date: datetime = None) -> List[Dict]:
        """Fetch articles from News API"""
        if not sources:
            sources = NEWS_SOURCES[:5]
        
        if not from_date:
            from_date = datetime.now() - timedelta(hours=24)
        
        if not to_date:
            to_date = datetime.now()
        
        all_articles = []
        
        for source in sources:
            try:
                params = {
                    'apiKey': self.api_key,
                    'sources': source,
                    'from': from_date.strftime('%Y-%m-%d'),
                    'to': to_date.strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'pageSize': 20
                }
                
                if query:
                    params['q'] = query
                
                response = requests.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'ok':
                    articles = data.get('articles', [])
                    logger.info(f"Fetched {len(articles)} articles from {source}")
                    all_articles.extend(articles)
                
                # Rate limiting
                time.sleep(0.1)
                
            except requests.RequestException as e:
                logger.error(f"Error fetching from {source}: {e}")
                continue
        
        return all_articles[:MAX_ARTICLES_PER_BATCH]
    
    def clean_article_text(self, text: str) -> str:
        """Clean article text by removing HTML and extra whitespace"""
        if not text:
            return ""
        
        # Basic HTML tag removal
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_source_name(self, source: Dict) -> str:
        """Extract source name from source object"""
        if isinstance(source, dict):
            return source.get('name', 'unknown')
        elif isinstance(source, str):
            return source
        else:
            return 'unknown'
    
    def store_articles(self, articles: List[Dict]) -> int:
        """Store articles in database"""
        stored_count = 0
        
        for article in articles:
            try:
                # Skip if already exists
                if self.db.article_exists(article['url']):
                    continue
                
                # Extract and clean data
                url = article.get('url', '')
                title = article.get('title', '').strip()
                text = self.clean_article_text(article.get('content', ''))
                
                if not title or not text or len(text) < 100:
                    continue
                
                source = self.extract_source_name(article.get('source', {}))
                author = article.get('author', '')
                
                published_at = None
                if article.get('publishedAt'):
                    try:
                        published_at = datetime.fromisoformat(
                            article['publishedAt'].replace('Z', '+00:00')
                        )
                    except ValueError:
                        published_at = datetime.now()
                
                article_id = self.db.insert_article(
                    url=url,
                    outlet=source,
                    title=title,
                    text=text,
                    author=author,
                    published_at=published_at
                )
                
                stored_count += 1
                logger.info(f"Stored article: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error storing article: {e}")
                continue
        
        return stored_count
    
    def run_ingestion(self, query: str = None, hours_back: int = 24):
        """Run the complete ingestion process"""
        logger.info("Starting news ingestion...")
        
        from_date = datetime.now() - timedelta(hours=hours_back)
        to_date = datetime.now()
        
        # Fetch articles
        articles = self.fetch_articles(
            query=query,
            from_date=from_date,
            to_date=to_date
        )
        
        logger.info(f"Fetched {len(articles)} articles from API")
        
        # Store articles
        stored_count = self.store_articles(articles)
        
        logger.info(f"Ingestion complete: {stored_count} new articles stored")
        return stored_count

def main():
    """Main function for running ingestion"""
    ingester = NewsIngester()
    
    demo_queries = [
        "election 2024",
        "climate change",
        "artificial intelligence",
        "economy inflation",
        "healthcare policy"
    ]
    
    total_stored = 0
    for query in demo_queries[:2]:
        logger.info(f"Fetching articles for query: {query}")
        stored = ingester.run_ingestion(query=query, hours_back=48)
        total_stored += stored
    
    logger.info(f"Total articles stored: {total_stored}")

if __name__ == "__main__":
    main()
