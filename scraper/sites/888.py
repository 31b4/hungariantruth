"""
Custom scraper for 888.hu
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Scraper888:
    def __init__(self, max_age_hours=24):
        self.base_url = "https://888.hu"
        self.max_age_hours = max_age_hours
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_articles(self, max_articles=10):
        """Fetch articles from 888.hu homepage"""
        articles = []
        
        try:
            logger.info(f"Scraping 888.hu")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try finding articles
            article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in str(x).lower() or 'post' in str(x).lower() or 'news' in str(x).lower()), limit=max_articles * 2)
            
            if not article_elements:
                article_elements = soup.find_all('a', href=lambda x: x and ('/hir/' in x or '/cikk/' in x), limit=max_articles * 2)
            
            seen_links = set()
            
            for element in article_elements:
                try:
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a', 'span'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    link_elem = element.find('a', href=True) if element.name != 'a' else element
                    if not link_elem:
                        continue
                    
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = self.base_url + link
                    elif not link.startswith('http'):
                        continue
                    
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    summary_elem = element.find(['p', 'div'], class_=lambda x: x and ('summary' in str(x).lower() or 'excerpt' in str(x).lower()))
                    summary = summary_elem.get_text(strip=True)[:500] if summary_elem else ""
                    
                    article = {
                        'source': '888',
                        'title': title,
                        'link': link,
                        'published': datetime.now().isoformat(),
                        'summary': summary
                    }
                    
                    if article['title'] and article['link']:
                        articles.append(article)
                        
                    if len(articles) >= max_articles:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from 888.hu")
            
        except Exception as e:
            logger.error(f"Error scraping 888.hu: {e}")
        
        return articles

