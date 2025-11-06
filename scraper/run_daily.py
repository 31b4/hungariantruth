#!/usr/bin/env python3
"""
Daily news aggregation and synthesis runner
This script is executed by GitHub Actions
"""
import sys
import logging
from datetime import datetime

from main import NewsAggregator
from gemini_synthesis import NewsSynthesizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function for daily news synthesis"""
    try:
        logger.info("=" * 60)
        logger.info(f"Hungarian Truth News - Daily Run - {datetime.now()}")
        logger.info("=" * 60)
        
        # Step 1: Scrape news from all sources
        logger.info("\n📰 Step 1: Scraping news sources...")
        aggregator = NewsAggregator()
        articles = aggregator.scrape_all_sources()
        
        if not articles:
            logger.error("❌ No articles collected! Cannot proceed.")
            sys.exit(1)
        
        # Save raw articles for debugging
        aggregator.save_raw_articles('raw_articles.json')
        
        # Step 2: Categorize articles
        logger.info("\n📊 Step 2: Categorizing articles...")
        categorized = aggregator.get_articles_by_category()
        logger.info(f"  Right-wing sources: {len(categorized['right_wing'])} articles")
        logger.info(f"  Left-wing sources: {len(categorized['left_wing'])} articles")
        logger.info(f"  Independent sources: {len(categorized['independent'])} articles")
        
        # Step 3: Synthesize with Gemini AI
        logger.info("\n🤖 Step 3: Synthesizing news with Gemini AI...")
        synthesizer = NewsSynthesizer()
        synthesis = synthesizer.synthesize(categorized)
        
        # Add today's date if not present
        if 'date' not in synthesis:
            synthesis['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Step 4: Save synthesis
        logger.info("\n💾 Step 4: Saving synthesis...")
        output_path = synthesizer.save_synthesis(synthesis)
        
        # Step 5: Update index.json for faster archive loading
        logger.info("\n📇 Step 5: Updating archive index...")
        try:
            from update_index import update_index
            update_index()
            logger.info("  ✓ Archive index updated")
        except Exception as e:
            logger.warning(f"  ⚠️  Could not update index: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Daily synthesis completed successfully!")
        logger.info(f"📄 Output saved to: {output_path}")
        logger.info(f"📰 Stories synthesized: {len(synthesis.get('stories', []))}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error during daily synthesis: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

