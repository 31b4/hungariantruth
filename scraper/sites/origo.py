"""
Custom scraper for Origo.hu
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OrigoScraper:
    def __init__(self, max_age_hours=24):
        self.base_url = "https://www.origo.hu"
        self.max_age_hours = max_age_hours
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_articles(self, max_articles=10):
        """
        Fetch articles from Origo.hu homepage
        
        Returns:
            List of article dictionaries with standardized format
        """
        articles = []
        
        try:
            logger.info(f"Scraping Origo.hu")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article elements - this is a placeholder structure
            # You'll need to inspect Origo's actual HTML to get the right selectors
            article_elements = soup.find_all('article', limit=max_articles)
            
            if not article_elements:
                # Try alternative selectors
                article_elements = soup.find_all('div', class_=['article-item', 'news-item'], limit=max_articles)
            
            for element in article_elements:
                try:
                    # Extract title
                    title_elem = element.find(['h1', 'h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = element.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = self.base_url + link
                    
                    # Extract summary if available
                    summary_elem = element.find(['p', 'div'], class_=['summary', 'lead', 'description'])
                    summary = summary_elem.get_text(strip=True)[:500] if summary_elem else ""
                    
                    article = {
                        'source': 'Origo',
                        'title': title,
                        'link': link,
                        'published': datetime.now().isoformat(),
                        'summary': summary
                    }
                    
                    if article['title'] and article['link']:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error parsing article element from Origo: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from Origo")
            
        except Exception as e:
            logger.error(f"Error scraping Origo.hu: {e}")
        
        return articles

