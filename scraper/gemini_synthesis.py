"""
Gemini AI integration for news synthesis
"""
import json
import logging
import os
from datetime import datetime
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
    
    def create_synthesis_prompt(self, categorized_articles):
        """
        Create a detailed prompt for Gemini to synthesize news
        
        Args:
            categorized_articles: Dictionary with articles grouped by political leaning
            
        Returns:
            Prompt string
        """
        prompt = """You are a professional journalist creating unbiased news synthesis for Hungarian readers.

You will receive news articles from different political perspectives:
- Right-wing/Government-aligned sources
- Left-wing/Opposition sources  
- Independent sources

Your task:
1. Identify the top 2-3 most important news stories of the day
2. For each story, analyze how different sources cover it
3. Create a neutral, fact-based synthesis that presents the truth without political bias
4. Provide both Hungarian and English versions
5. Cite which sources reported what

IMPORTANT: You MUST return ONLY valid, complete JSON. Do not truncate. Complete all fields.

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
      "summary_hu": "Detailed neutral summary in Hungarian (2-3 paragraphs)",
      "summary_en": "Detailed neutral summary in English (2-3 paragraphs)",
      "sources_analyzed": ["Source1", "Source2"],
      "perspective_comparison": "How different sources covered this (1 paragraph)",
      "key_facts": ["Fact 1", "Fact 2", "Fact 3"]
    }
  ],
  "methodology_note_hu": "Brief note on synthesis methodology in Hungarian",
  "methodology_note_en": "Brief note on synthesis methodology in English"
}

Here are today's articles:

"""
        
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
    
    def synthesize(self, categorized_articles, retry_count=3):
        """
        Use Gemini to synthesize news from multiple perspectives
        
        Args:
            categorized_articles: Dictionary with articles grouped by political leaning
            retry_count: Number of retries if API fails
            
        Returns:
            Dictionary with synthesized news
        """
        prompt = self.create_synthesis_prompt(categorized_articles)
        
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

