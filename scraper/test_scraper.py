#!/usr/bin/env python3
"""
Simple test script to verify scraper functionality
"""
import sys
from rss_reader import RSSReader
from sites.origo import OrigoScraper

def test_rss_reader():
    """Test RSS feed reading"""
    print("\n=== Testing RSS Reader ===")
    reader = RSSReader(max_age_hours=24)
    
    # Test with Telex
    print("\n📰 Testing Telex RSS feed...")
    articles = reader.fetch_articles(
        "https://telex.hu/rss",
        "Telex",
        max_articles=3
    )
    
    if articles:
        print(f"✅ Successfully fetched {len(articles)} articles from Telex")
        print(f"First article: {articles[0]['title'][:60]}...")
    else:
        print("⚠️  No articles fetched from Telex")
    
    return len(articles) > 0

def test_custom_scraper():
    """Test custom scraper"""
    print("\n=== Testing Custom Scraper ===")
    scraper = OrigoScraper(max_age_hours=24)
    
    print("\n📰 Testing Origo scraper...")
    articles = scraper.fetch_articles(max_articles=3)
    
    if articles:
        print(f"✅ Successfully scraped {len(articles)} articles from Origo")
        print(f"First article: {articles[0]['title'][:60]}...")
    else:
        print("⚠️  No articles scraped from Origo")
    
    return len(articles) > 0

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 Hungarian Truth News - Scraper Test")
    print("=" * 60)
    
    results = []
    
    # Test RSS reader
    results.append(test_rss_reader())
    
    # Test custom scraper
    results.append(test_custom_scraper())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"RSS Reader: {'✅ PASSED' if results[0] else '❌ FAILED'}")
    print(f"Custom Scraper: {'✅ PASSED' if results[1] else '❌ FAILED'}")
    
    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

