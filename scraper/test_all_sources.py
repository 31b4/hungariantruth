#!/usr/bin/env python3
"""
Test all news sources to see which RSS feeds work and which need custom scrapers
"""
import json
import sys
import importlib
from rss_reader import RSSReader
from sites.origo import OrigoScraper
from sites.magyar_hirlap import MagyarHirlapScraper
from sites.pestisracok import PestiSracokScraper
from sites.hirado import HiradoScraper
from sites.rtl import RTLScraper
from sites.partizan import PartizanScraper
from sites.direkt36 import Direkt36Scraper

def test_rss_feed(rss_url, source_name):
    """Test if an RSS feed is accessible and parseable"""
    try:
        reader = RSSReader(max_age_hours=24)
        articles = reader.fetch_articles(rss_url, source_name, max_articles=3)
        
        if articles and len(articles) > 0:
            return {
                'status': '✅ WORKS',
                'articles': len(articles),
                'sample_title': articles[0]['title'][:60] + '...' if articles[0]['title'] else 'N/A'
            }
        else:
            return {
                'status': '⚠️  NO ARTICLES',
                'articles': 0,
                'sample_title': 'N/A'
            }
    except Exception as e:
        return {
            'status': '❌ FAILED',
            'articles': 0,
            'sample_title': f'Error: {str(e)[:50]}'
        }

def test_custom_scraper(scraper_name, source_name):
    """Test custom scrapers"""
    try:
        # Map of scraper names to classes
        scraper_map = {
            'origo': OrigoScraper,
            'magyar_hirlap': MagyarHirlapScraper,
            'pestisracok': PestiSracokScraper,
            'hirado': HiradoScraper,
            'rtl': RTLScraper,
            'partizan': PartizanScraper,
            'direkt36': Direkt36Scraper,
        }
        
        # Handle modules that start with numbers
        if scraper_name == '888':
            module = importlib.import_module('sites.888', package=None)
            ScraperClass = getattr(module, 'Scraper888')
            scraper = ScraperClass(max_age_hours=24)
        elif scraper_name in scraper_map:
            scraper = scraper_map[scraper_name](max_age_hours=24)
        else:
            return {
                'status': '❓ UNKNOWN SCRAPER',
                'articles': 0,
                'sample_title': f'Scraper "{scraper_name}" not implemented'
            }
        
        articles = scraper.fetch_articles(max_articles=3)
        
        if articles and len(articles) > 0:
            return {
                'status': '✅ WORKS',
                'articles': len(articles),
                'sample_title': articles[0]['title'][:60] + '...' if articles[0]['title'] else 'N/A'
            }
        else:
            return {
                'status': '⚠️  NO ARTICLES',
                'articles': 0,
                'sample_title': 'N/A'
            }
    except Exception as e:
        return {
            'status': '❌ FAILED',
            'articles': 0,
            'sample_title': f'Error: {str(e)[:50]}'
        }

def main():
    """Test all sources"""
    print("=" * 80)
    print("Testing All Hungarian News Sources")
    print("=" * 80)
    print()
    
    # Load config
    try:
        with open('config_sources.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    results = {
        'right_wing': [],
        'left_wing': [],
        'independent': []
    }
    
    total_sources = 0
    working_sources = 0
    failed_sources = 0
    
    # Test each category
    for category_name, sources in config['sources'].items():
        print(f"\n{'=' * 80}")
        print(f"Testing {category_name.upper().replace('_', ' ')} Sources")
        print(f"{'=' * 80}\n")
        
        for source_config in sources:
            total_sources += 1
            source_name = source_config['name']
            source_type = source_config['type']
            
            print(f"Testing: {source_name} ({source_config['url']})", end=" ... ")
            sys.stdout.flush()
            
            if source_type == 'rss':
                rss_url = source_config['rss_url']
                result = test_rss_feed(rss_url, source_name)
                print(result['status'])
                
                if result['status'] == '✅ WORKS':
                    working_sources += 1
                else:
                    failed_sources += 1
                
                results[category_name].append({
                    'name': source_name,
                    'url': source_config['url'],
                    'type': 'rss',
                    'rss_url': rss_url,
                    **result
                })
                
            elif source_type == 'custom':
                scraper_name = source_config['scraper']
                result = test_custom_scraper(scraper_name, source_name)
                print(result['status'])
                
                if result['status'] == '✅ WORKS':
                    working_sources += 1
                else:
                    failed_sources += 1
                
                results[category_name].append({
                    'name': source_name,
                    'url': source_config['url'],
                    'type': 'custom',
                    'scraper': scraper_name,
                    **result
                })
            
            if result.get('sample_title'):
                print(f"  └─ Sample: {result['sample_title']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal Sources: {total_sources}")
    print(f"✅ Working: {working_sources}")
    print(f"❌ Failed/No Articles: {failed_sources}")
    print(f"Success Rate: {(working_sources/total_sources*100):.1f}%")
    
    # List failed sources
    print("\n" + "=" * 80)
    print("FAILED SOURCES (Need Custom Scrapers)")
    print("=" * 80)
    
    failed_list = []
    for category, sources in results.items():
        for source in sources:
            if source['status'] != '✅ WORKS':
                failed_list.append(source)
    
    if failed_list:
        for source in failed_list:
            print(f"\n❌ {source['name']} ({source['url']})")
            print(f"   Type: {source['type']}")
            if source['type'] == 'rss':
                print(f"   RSS URL: {source.get('rss_url', 'N/A')}")
            print(f"   Issue: {source.get('sample_title', 'Unknown')}")
    else:
        print("\n✅ All sources are working!")
    
    # List working sources
    print("\n" + "=" * 80)
    print("WORKING SOURCES")
    print("=" * 80)
    
    working_list = []
    for category, sources in results.items():
        for source in sources:
            if source['status'] == '✅ WORKS':
                working_list.append(source)
    
    print(f"\n✅ {len(working_list)} sources working:")
    for source in working_list:
        print(f"   • {source['name']} ({source['articles']} articles tested)")
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()

