"""
RSS feed reader for news sources
"""
import feedparser
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSReader:
    def __init__(self, max_age_hours=24):
        self.max_age_hours = max_age_hours
    
    def fetch_articles(self, rss_url, source_name, max_articles=10):
        """
        Fetch articles from an RSS feed
        
        Args:
            rss_url: URL of the RSS feed
            source_name: Name of the news source
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries with standardized format
        """
        articles = []
        
        try:
            logger.info(f"Fetching RSS feed from {source_name}: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing warning for {source_name}: {feed.bozo_exception}")
            
            cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
            
            for entry in feed.entries[:max_articles]:
                try:
                    # Parse published date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        try:
                            pub_date = date_parser.parse(entry.published)
                        except:
                            pass
                    
                    # Skip if too old
                    if pub_date and pub_date < cutoff_time:
                        continue
                    
                    # Extract article data
                    article = {
                        'source': source_name,
                        'title': entry.get('title', '').strip(),
                        'link': entry.get('link', ''),
                        'published': pub_date.isoformat() if pub_date else None,
                        'summary': entry.get('summary', '').strip()[:500],  # Limit summary length
                    }
                    
                    if article['title'] and article['link']:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source_name}: {e}")
        
        return articles

