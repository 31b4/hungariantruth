"""
Main scraper orchestrator for Hungarian Truth News
"""
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

from rss_reader import RSSReader
from sites.origo import OrigoScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsAggregator:
    def __init__(self, config_path='config_sources.json'):
        """Initialize the news aggregator"""
        self.config = self._load_config(config_path)
        self.rss_reader = RSSReader(
            max_age_hours=self.config['scraping_settings']['max_article_age_hours']
        )
        self.articles = []
    
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)
    
    def scrape_all_sources(self):
        """Scrape articles from all configured sources"""
        max_articles = self.config['scraping_settings']['max_articles_per_source']
        
        # Process all source categories
        for category_name, sources in self.config['sources'].items():
            logger.info(f"\n=== Scraping {category_name} sources ===")
            
            for source_config in sources:
                try:
                    source_name = source_config['name']
                    source_type = source_config['type']
                    
                    if source_type == 'rss':
                        # Use RSS reader
                        rss_url = source_config['rss_url']
                        articles = self.rss_reader.fetch_articles(
                            rss_url, 
                            source_name, 
                            max_articles
                        )
                        self.articles.extend(articles)
                        
                    elif source_type == 'custom':
                        # Use custom scraper
                        scraper_name = source_config['scraper']
                        if scraper_name == 'origo':
                            scraper = OrigoScraper(
                                max_age_hours=self.config['scraping_settings']['max_article_age_hours']
                            )
                            articles = scraper.fetch_articles(max_articles)
                            self.articles.extend(articles)
                        else:
                            logger.warning(f"Unknown custom scraper: {scraper_name}")
                    
                except Exception as e:
                    logger.error(f"Error scraping {source_config.get('name', 'unknown')}: {e}")
                    continue
        
        logger.info(f"\n=== Total articles collected: {len(self.articles)} ===")
        return self.articles
    
    def get_articles_by_category(self):
        """Group articles by their source category"""
        categorized = {
            'right_wing': [],
            'left_wing': [],
            'independent': []
        }
        
        # Create a mapping of source names to categories
        source_to_category = {}
        for category, sources in self.config['sources'].items():
            for source in sources:
                source_to_category[source['name']] = category
        
        # Categorize articles
        for article in self.articles:
            category = source_to_category.get(article['source'], 'independent')
            categorized[category].append(article)
        
        return categorized
    
    def save_raw_articles(self, output_path='raw_articles.json'):
        """Save raw scraped articles to JSON file"""
        try:
            data = {
                'scrape_date': datetime.now().isoformat(),
                'total_articles': len(self.articles),
                'articles': self.articles,
                'by_category': self.get_articles_by_category()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved raw articles to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving raw articles: {e}")
            return None


def main():
    """Main execution function"""
    logger.info("=== Starting Hungarian Truth News Scraper ===")
    
    # Initialize aggregator
    aggregator = NewsAggregator()
    
    # Scrape all sources
    articles = aggregator.scrape_all_sources()
    
    if not articles:
        logger.error("No articles collected! Exiting.")
        sys.exit(1)
    
    # Save raw articles
    aggregator.save_raw_articles()
    
    logger.info("=== Scraping completed successfully ===")
    
    return articles


if __name__ == '__main__':
    main()

