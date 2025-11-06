"""
Gemini AI integration for news synthesis
"""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
import google.generativeai as genai

logger = logging.getLogger(__name__)


class NewsSynthesizer:
    def __init__(self, api_key=None):
        """
        Initialize Gemini AI synthesizer
        
        Args:
            api_key: Gemini API key (if None, reads from GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def load_previous_stories(self, days_back=3, max_stories_per_day=3):
        """
        Load previous days' stories to avoid repetition
        
        Args:
            days_back: Number of previous days to load
            max_stories_per_day: Maximum stories to include per day
            
        Returns:
            List of previous stories
        """
        previous_stories = []
        
        # Try multiple possible paths (local dev vs GitHub Actions)
        possible_paths = [
            Path('../data'),
            Path('data'),
            Path(__file__).parent.parent / 'data',
        ]
        
        data_dir = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                data_dir = path
                break
        
        if not data_dir:
            logger.warning("Could not find data directory, skipping previous stories")
            return previous_stories
        
        for i in range(1, days_back + 1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            filepath = data_dir / f"{date_str}.json"
            
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        stories = data.get('stories', [])[:max_stories_per_day]
                        for story in stories:
                            story['previous_date'] = date_str
                        previous_stories.extend(stories)
                        logger.info(f"Loaded {len(stories)} stories from {date_str}")
                except Exception as e:
                    logger.warning(f"Could not load {date_str}.json: {e}")
        
        return previous_stories
    
    def create_synthesis_prompt(self, categorized_articles, previous_stories=None):
        """
        Create a detailed prompt for Gemini to synthesize news
        
        Args:
            categorized_articles: Dictionary with articles grouped by political leaning
            previous_stories: List of stories from previous days
            
        Returns:
            Prompt string
        """
        prompt = """You are a professional journalist creating unbiased news synthesis for Hungarian readers.

You will receive:
1. News articles from today from different political perspectives
2. Previous days' stories (to avoid repetition and identify ongoing stories)

Your task:
1. Identify NEW important stories that haven't been covered in previous days
2. Identify ONGOING stories from previous days that have new developments
3. For ongoing stories, provide UPDATES (what's new today) rather than repeating old information
4. For each story, analyze how different sources cover it
5. Create a neutral, fact-based synthesis that presents the truth without political bias
6. Provide both Hungarian and English versions
7. Cite which sources reported what

IMPORTANT: 
- Do NOT repeat stories from previous days unless there are significant new developments
- For ongoing stories, focus on what's NEW today
- You MUST return ONLY valid, complete JSON. Do not truncate. Complete all fields.

Guidelines:
- Be strictly neutral and objective
- Focus on verifiable facts
- Note when sources disagree on facts vs. interpretation
- Avoid inflammatory language
- Present multiple perspectives fairly
- If only one side reports something, note this explicitly

Output format: JSON with this structure:
{
  "date": "YYYY-MM-DD",
  "stories": [
    {
      "title_hu": "Hungarian title",
      "title_en": "English title",
      "summary_hu": "Detailed neutral summary in Hungarian (2-3 paragraphs). For ongoing stories, focus on NEW developments.",
      "summary_en": "Detailed neutral summary in English (2-3 paragraphs). For ongoing stories, focus on NEW developments.",
      "sources_analyzed": ["Source1", "Source2"],
      "perspective_comparison": "How different sources covered this (1 paragraph)",
      "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
      "is_ongoing": true/false,
      "previous_date": "YYYY-MM-DD" (only if this is an update to a previous story)
    }
  ],
  "methodology_note_hu": "Brief note on synthesis methodology in Hungarian",
  "methodology_note_en": "Brief note on synthesis methodology in English"
}

"""
        
        # Add previous stories if available
        if previous_stories:
            prompt += "\n=== PREVIOUS DAYS' STORIES (for context - avoid repetition) ===\n"
            for story in previous_stories:
                prompt += f"\nDate: {story.get('previous_date', 'Unknown')}\n"
                prompt += f"Title: {story.get('title_hu', story.get('title_en', 'N/A'))}\n"
                # Include just key facts to save tokens
                key_facts = story.get('key_facts', [])
                if key_facts:
                    prompt += f"Key Facts: {', '.join(key_facts[:3])}\n"
                prompt += "\n"
        
        prompt += "\n=== TODAY'S ARTICLES ===\n"
        
        # Add right-wing articles
        prompt += "\n=== RIGHT-WING/GOVERNMENT SOURCES ===\n"
        for article in categorized_articles.get('right_wing', []):
            prompt += f"\nSource: {article['source']}\n"
            prompt += f"Title: {article['title']}\n"
            if article.get('summary'):
                prompt += f"Summary: {article['summary']}\n"
            prompt += f"Link: {article['link']}\n"
        
        # Add left-wing articles
        prompt += "\n\n=== LEFT-WING/OPPOSITION SOURCES ===\n"
        for article in categorized_articles.get('left_wing', []):
            prompt += f"\nSource: {article['source']}\n"
            prompt += f"Title: {article['title']}\n"
            if article.get('summary'):
                prompt += f"Summary: {article['summary']}\n"
            prompt += f"Link: {article['link']}\n"
        
        # Add independent articles
        prompt += "\n\n=== INDEPENDENT SOURCES ===\n"
        for article in categorized_articles.get('independent', []):
            prompt += f"\nSource: {article['source']}\n"
            prompt += f"Title: {article['title']}\n"
            if article.get('summary'):
                prompt += f"Summary: {article['summary']}\n"
            prompt += f"Link: {article['link']}\n"
        
        prompt += "\n\nNow create the neutral synthesis in JSON format:"
        
        return prompt
    
    def synthesize(self, categorized_articles, retry_count=3, include_previous_days=True):
        """
        Use Gemini to synthesize news from multiple perspectives
        
        Args:
            categorized_articles: Dictionary with articles grouped by political leaning
            retry_count: Number of retries if API fails
            include_previous_days: Whether to include previous days' stories for context
            
        Returns:
            Dictionary with synthesized news
        """
        # Load previous stories if requested
        previous_stories = None
        if include_previous_days:
            try:
                previous_stories = self.load_previous_stories(days_back=3, max_stories_per_day=3)
                logger.info(f"Loaded {len(previous_stories)} previous stories for context")
            except Exception as e:
                logger.warning(f"Could not load previous stories: {e}")
        
        prompt = self.create_synthesis_prompt(categorized_articles, previous_stories)
        
        # Estimate token usage (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) / 4
        logger.info(f"Estimated prompt tokens: ~{int(estimated_tokens):,} (Gemini 2.5 Flash limit: 1,000,000)")
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Sending synthesis request to Gemini (attempt {attempt + 1}/{retry_count})")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.3,  # Lower temperature for more factual output
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 8192,
                    }
                )
                
                # Extract JSON from response
                try:
                    response_text = response.text
                except ValueError:
                    # Handle complex responses
                    response_text = response.candidates[0].content.parts[0].text
                
                # Try to parse JSON (handle markdown code blocks)
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    json_text = response_text[start:end].strip()
                elif '```' in response_text:
                    start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    json_text = response_text[start:end].strip()
                else:
                    json_text = response_text.strip()
                
                synthesis = json.loads(json_text)
                
                # Add metadata
                synthesis['metadata'] = {
                    'sources_scraped': sum(len(articles) for articles in categorized_articles.values()),
                    'generation_time': datetime.now().isoformat(),
                    'ai_model': 'gemini-2.5-flash'
                }
                
                logger.info(f"Successfully synthesized {len(synthesis.get('stories', []))} stories")
                
                return synthesis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Gemini response: {e}")
                logger.error(f"Response text length: {len(response_text)}")
                logger.error(f"First 1000 chars: {response_text[:1000]}")
                logger.error(f"Last 500 chars: {response_text[-500:]}")
                if attempt < retry_count - 1:
                    logger.info("Retrying with simplified request...")
                    continue
                else:
                    # Save problematic response for debugging
                    with open('gemini_error_response.txt', 'w', encoding='utf-8') as f:
                        f.write(response_text)
                    logger.error("Saved problematic response to gemini_error_response.txt")
                    raise
                    
            except Exception as e:
                logger.error(f"Error during synthesis: {e}")
                if attempt < retry_count - 1:
                    continue
                else:
                    raise
        
        raise Exception("Failed to synthesize news after multiple attempts")
    
    def save_synthesis(self, synthesis, output_dir='../data'):
        """
        Save synthesis to dated JSON file
        
        Args:
            synthesis: Synthesized news dictionary
            output_dir: Directory to save output
            
        Returns:
            Path to saved file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename
            date_str = synthesis.get('date', datetime.now().strftime('%Y-%m-%d'))
            filename = f"{date_str}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(synthesis, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved synthesis to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving synthesis: {e}")
            raise

