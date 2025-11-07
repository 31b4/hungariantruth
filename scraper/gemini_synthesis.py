"""
Gemini AI integration for news synthesis
"""
import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import google.generativeai as genai

logger = logging.getLogger(__name__)


def repair_json(json_text):
    """
    Attempt to repair common JSON issues from AI responses:
    - Unterminated strings
    - Missing closing brackets/braces
    - Unescaped newlines in strings
    """
    # Simple approach: find the last complete JSON structure
    # Look for the last complete closing brace
    last_brace = json_text.rfind('}')
    if last_brace == -1:
        # No closing brace at all, try to add one
        # Find the last opening brace
        last_open = json_text.rfind('{')
        if last_open != -1:
            # Add closing for any open structures
            open_count = json_text.count('{') - json_text.count('}')
            if open_count > 0:
                json_text += '\n' + '}' * open_count
        return json_text
    
    # Find the matching opening brace
    brace_count = 0
    start_pos = last_brace
    for i in range(last_brace, -1, -1):
        if json_text[i] == '}':
            brace_count += 1
        elif json_text[i] == '{':
            brace_count -= 1
            if brace_count == 0:
                start_pos = i
                break
    
    # Extract the complete JSON object
    if start_pos < last_brace:
        json_text = json_text[start_pos:last_brace + 1]
    
    # Try to close any unterminated strings at the end
    # Simple heuristic: if the last non-whitespace character before } is not ", ], or }, 
    # and we're inside quotes, close the quote
    lines = json_text.split('\n')
    if lines:
        last_line = lines[-1].rstrip()
        # Check if we're likely in an unterminated string
        # Count quotes in the last line
        quote_count = last_line.count('"') - last_line.count('\\"')
        if quote_count % 2 == 1:  # Odd number of quotes means unterminated
            # Try to find where to close it
            # Look for the last field that might be incomplete
            if not last_line.endswith(('"', '}', ']', ',')):
                # Likely an unterminated string, try to close it
                lines[-1] = last_line + '"'
                json_text = '\n'.join(lines)
    
    # Try to close incomplete JSON structures
    open_braces = json_text.count('{')
    close_braces = json_text.count('}')
    open_brackets = json_text.count('[')
    close_brackets = json_text.count(']')
    
    # Add missing closing brackets/braces (but be careful not to over-close)
    if open_braces > close_braces:
        json_text += '\n' + '}' * (open_braces - close_braces)
    if open_brackets > close_brackets:
        json_text += '\n' + ']' * (open_brackets - close_brackets)
    
    return json_text


def extract_and_repair_json(response_text):
    """
    Extract JSON from response and attempt to repair it
    """
    # Extract JSON from markdown code blocks if present
    if '```json' in response_text:
        start = response_text.find('```json') + 7
        end = response_text.find('```', start)
        if end == -1:
            # Unterminated code block, try to find end of JSON
            json_text = response_text[start:].strip()
        else:
            json_text = response_text[start:end].strip()
    elif '```' in response_text:
        start = response_text.find('```') + 3
        end = response_text.find('```', start)
        if end == -1:
            json_text = response_text[start:].strip()
        else:
            json_text = response_text[start:end].strip()
    else:
        json_text = response_text.strip()
    
    # Try to find JSON object boundaries
    first_brace = json_text.find('{')
    if first_brace != -1:
        # Find the last complete closing brace
        last_brace = json_text.rfind('}')
        if last_brace != -1 and last_brace > first_brace:
            json_text = json_text[first_brace:last_brace + 1]
        else:
            # No closing brace, try to repair
            json_text = json_text[first_brace:]
    
    # Attempt repair
    repaired = repair_json(json_text)
    
    return repaired


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

CRITICAL JSON REQUIREMENTS:
- You MUST return ONLY valid, complete JSON
- Do NOT truncate any strings - complete all summaries fully
- Escape all quotes and special characters properly (use \\" for quotes inside strings)
- Close all strings, arrays, and objects properly
- If you run out of space, shorten summaries rather than truncating mid-string
- Test that your JSON is valid before returning it

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
      "summary_hu": "Concise neutral summary in Hungarian (1-2 paragraphs, max 500 words). For ongoing stories, focus on NEW developments.",
      "summary_en": "Concise neutral summary in English (1-2 paragraphs, max 500 words). For ongoing stories, focus on NEW developments.",
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
                
                # Extract and repair JSON
                json_text = extract_and_repair_json(response_text)
                
                # Try to parse the repaired JSON
                try:
                    synthesis = json.loads(json_text)
                except json.JSONDecodeError as parse_error:
                    # If repair didn't work, try a more aggressive approach
                    logger.warning(f"Initial JSON parse failed: {parse_error}. Attempting aggressive repair...")
                    
                    # Try to find the stories array start
                    stories_start = json_text.find('"stories"')
                    if stories_start != -1:
                        # Find the opening bracket after "stories"
                        bracket_start = json_text.find('[', stories_start)
                        if bracket_start != -1:
                            # Try to find complete story objects
                            # Look for patterns like {"title_hu": ...}
                            story_pattern = r'\{\s*"title_hu"\s*:'
                            story_matches = list(re.finditer(story_pattern, json_text[bracket_start:], re.MULTILINE))
                            
                            if story_matches:
                                # Try to extract each story object
                                stories = []
                                for i, match in enumerate(story_matches):
                                    start_pos = bracket_start + match.start()
                                    # Find the end of this story object
                                    if i + 1 < len(story_matches):
                                        end_pos = bracket_start + story_matches[i + 1].start()
                                    else:
                                        # Last story, find the closing brace
                                        end_pos = json_text.find('}', start_pos)
                                        if end_pos == -1:
                                            end_pos = len(json_text)
                                        else:
                                            end_pos += 1
                                    
                                    story_text = json_text[start_pos:end_pos].rstrip().rstrip(',')
                                    # Try to close it if incomplete
                                    if not story_text.rstrip().endswith('}'):
                                        story_text = story_text.rstrip().rstrip(',') + '\n}'
                                    
                                    try:
                                        story = json.loads(story_text)
                                        stories.append(story)
                                    except:
                                        # Skip this story if it's too broken
                                        logger.warning(f"Could not parse story {i+1}, skipping...")
                                        continue
                                
                                if stories:
                                    # Build a minimal valid JSON
                                    date_match = re.search(r'"date"\s*:\s*"([^"]+)"', json_text)
                                    date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
                                    
                                    synthesis = {
                                        'date': date_str,
                                        'stories': stories,
                                        'methodology_note_hu': 'Automatikusan generálva (javított JSON)',
                                        'methodology_note_en': 'Automatically generated (repaired JSON)'
                                    }
                                    logger.info(f"Successfully extracted {len(stories)} stories using aggressive repair")
                                else:
                                    raise parse_error
                            else:
                                raise parse_error
                        else:
                            raise parse_error
                    else:
                        raise parse_error
                
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

