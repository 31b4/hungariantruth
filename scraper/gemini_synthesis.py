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
    # First, try to find and close unterminated strings
    # We'll scan through the text and track string state
    result = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(json_text):
        char = json_text[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        if char == '"':
            result.append(char)
            in_string = not in_string
            i += 1
            continue
        
        result.append(char)
        i += 1
    
    # If we ended inside a string, close it
    if in_string:
        result.append('"')
    
    json_text = ''.join(result)
    
    # Now try to find the last complete JSON structure
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
    
    # Find the matching opening brace by counting backwards
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
    
    def create_synthesis_prompt(self, categorized_articles, previous_stories=None, max_stories=2):
        """
        Create a detailed prompt for Gemini to synthesize news
        
        Args:
            categorized_articles: Dictionary with articles grouped by political leaning
            previous_stories: List of stories from previous days
            max_stories: Maximum number of stories to generate (default 2)
            
        Returns:
            Prompt string
        """
        prompt = """You are a professional journalist creating unbiased news synthesis for Hungarian readers.

You will receive:
1. News articles from today from different political perspectives
2. Previous days' stories (to avoid repetition and identify ongoing stories)

Your task:
1. Identify the MOST IMPORTANT new stories that haven't been covered in previous days
2. Identify ONGOING stories from previous days that have significant new developments
3. For ongoing stories, provide UPDATES (what's new today) rather than repeating old information
4. For each story, analyze how different sources cover it
5. Create a neutral, fact-based synthesis that presents the truth without political bias
6. Provide both Hungarian and English versions
7. Cite which sources reported what

CRITICAL JSON REQUIREMENTS:
- You MUST return ONLY valid, complete JSON
- Return MAXIMUM {max_stories} stories total (prioritize the most important ones)
- Do NOT truncate any strings - complete all summaries fully
- Keep summaries SHORT (max 250 words per summary) to ensure you don't run out of tokens
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
      "summary_hu": "Concise neutral summary in Hungarian (1 paragraph, max 250 words). For ongoing stories, focus on NEW developments.",
      "summary_en": "Concise neutral summary in English (1 paragraph, max 250 words). For ongoing stories, focus on NEW developments.",
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
        
        # Replace {max_stories} placeholder (escape other braces first)
        prompt = prompt.replace('{max_stories}', str(max_stories))
        
        return prompt
    
    def identify_stories(self, categorized_articles, previous_stories=None, max_stories=3):
        """
        Step 1: Identify which stories to cover based on today's articles
        
        Returns:
            List of story identifiers with titles and brief descriptions
        """
        prompt = """You are analyzing today's news to identify the most important stories to cover.

You will receive:
1. News articles from today from different political perspectives
2. Previous days' stories (to avoid repetition)

Your task:
1. Identify the {max_stories} MOST IMPORTANT new stories that haven't been covered in previous days
2. Identify 0-1 ONGOING stories from previous days that have significant new developments
3. For each story, provide just a brief identifier

Return ONLY valid JSON in this format:
{{
  "stories_to_cover": [
    {{
      "story_id": 1,
      "title_hu": "Brief Hungarian title",
      "title_en": "Brief English title",
      "is_ongoing": false,
      "previous_date": null
    }},
    {{
      "story_id": 2,
      "title_hu": "Brief Hungarian title",
      "title_en": "Brief English title",
      "is_ongoing": true,
      "previous_date": "2025-11-05"
    }}
  ]
}}

CRITICAL: Return ONLY the JSON, no other text. Maximum {max_stories} stories.

"""
        
        # Add previous stories if available
        if previous_stories:
            prompt += "\n=== PREVIOUS DAYS' STORIES (for context - avoid repetition) ===\n"
            for story in previous_stories:
                prompt += f"\nDate: {story.get('previous_date', 'Unknown')}\n"
                prompt += f"Title: {story.get('title_hu', story.get('title_en', 'N/A'))}\n"
                key_facts = story.get('key_facts', [])
                if key_facts:
                    prompt += f"Key Facts: {', '.join(key_facts[:3])}\n"
                prompt += "\n"
        
        prompt += "\n=== TODAY'S ARTICLES ===\n"
        
        # Add articles (just titles to save tokens)
        prompt += "\n=== RIGHT-WING/GOVERNMENT SOURCES ===\n"
        for article in categorized_articles.get('right_wing', [])[:30]:  # Limit to save tokens
            prompt += f"{article['source']}: {article['title']}\n"
        
        prompt += "\n=== LEFT-WING/OPPOSITION SOURCES ===\n"
        for article in categorized_articles.get('left_wing', [])[:30]:
            prompt += f"{article['source']}: {article['title']}\n"
        
        prompt += "\n=== INDEPENDENT SOURCES ===\n"
        for article in categorized_articles.get('independent', [])[:20]:
            prompt += f"{article['source']}: {article['title']}\n"
        
        prompt += "\n\nNow identify the stories to cover (JSON format only):"
        
        # Replace placeholders (escape other braces first)
        prompt = prompt.replace('{max_stories}', str(max_stories))
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,  # Small response for story identification
                }
            )
            
            # Extract JSON
            response_text = None
            try:
                response_text = response.text
            except ValueError:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            response_text = ''.join(text_parts)
            
            if not response_text:
                raise ValueError("Could not extract text from Gemini response")
            
            # Extract and parse JSON
            json_text = extract_and_repair_json(response_text)
            result = json.loads(json_text)
            
            return result.get('stories_to_cover', [])
            
        except Exception as e:
            logger.error(f"Error identifying stories: {e}")
            # Fallback: return empty list, will generate 1 default story
            return []
    
    def generate_single_story(self, story_info, categorized_articles, previous_stories=None):
        """
        Step 2: Generate a single story in full detail
        
        Args:
            story_info: Dictionary with story_id, title_hu, title_en, is_ongoing, previous_date
            categorized_articles: Dictionary with articles grouped by political leaning
            previous_stories: List of stories from previous days
            
        Returns:
            Complete story dictionary
        """
        prompt = """You are a professional journalist creating an unbiased news synthesis for one specific story.

Story to synthesize:
- Hungarian Title: {title_hu}
- English Title: {title_en}
- Is Ongoing: {is_ongoing}
- Previous Date: {previous_date}

Your task:
1. Find all articles related to this story from different political perspectives
2. Create a neutral, fact-based synthesis
3. Analyze how different sources cover it
4. Provide both Hungarian and English versions

CRITICAL JSON REQUIREMENTS:
- You MUST return ONLY valid, complete JSON
- Do NOT truncate any strings - complete all summaries fully
- Keep summaries concise (max 300 words per summary)
- Escape all quotes properly (use \\" for quotes inside strings)
- Close all strings, arrays, and objects properly

Return ONLY valid JSON in this format:
{{
  "title_hu": "Hungarian title",
  "title_en": "English title",
  "summary_hu": "Detailed neutral summary in Hungarian (1-2 paragraphs, max 300 words). For ongoing stories, focus on NEW developments.",
  "summary_en": "Detailed neutral summary in English (1-2 paragraphs, max 300 words). For ongoing stories, focus on NEW developments.",
  "sources_analyzed": ["Source1", "Source2"],
  "perspective_comparison": "How different sources covered this (1 paragraph)",
  "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
  "is_ongoing": {is_ongoing},
  "previous_date": {previous_date_json}
}}

"""
        
        # Add relevant articles (filter by title keywords)
        title_keywords = story_info.get('title_hu', '').lower().split()[:3]  # Use first 3 words
        
        prompt += "\n=== RELEVANT ARTICLES ===\n"
        relevant_count = 0
        
        for category in ['right_wing', 'left_wing', 'independent']:
            prompt += f"\n=== {category.upper().replace('_', '-')} SOURCES ===\n"
            for article in categorized_articles.get(category, []):
                # Simple keyword matching
                article_title_lower = article['title'].lower()
                if any(keyword in article_title_lower for keyword in title_keywords) or relevant_count < 15:
                    prompt += f"\nSource: {article['source']}\n"
                    prompt += f"Title: {article['title']}\n"
                    if article.get('summary'):
                        prompt += f"Summary: {article['summary'][:200]}...\n"  # Truncate summaries
                    prompt += f"Link: {article['link']}\n"
                    relevant_count += 1
                    if relevant_count >= 30:  # Limit total articles
                        break
            if relevant_count >= 30:
                break
        
        # Add previous story context if ongoing
        if story_info.get('is_ongoing') and previous_stories:
            previous_date = story_info.get('previous_date')
            if previous_date:
                for story in previous_stories:
                    if story.get('previous_date') == previous_date:
                        prompt += f"\n=== PREVIOUS STORY CONTEXT ===\n"
                        prompt += f"Title: {story.get('title_hu', story.get('title_en', 'N/A'))}\n"
                        key_facts = story.get('key_facts', [])
                        if key_facts:
                            prompt += f"Previous Key Facts: {', '.join(key_facts[:5])}\n"
                        break
        
        prompt += "\n\nNow create the synthesis for this story (JSON format only):"
        
        # Format the prompt
        previous_date_json = f'"{story_info.get("previous_date")}"' if story_info.get('previous_date') else 'null'
        prompt = prompt.format(
            title_hu=story_info.get('title_hu', ''),
            title_en=story_info.get('title_en', ''),
            is_ongoing=str(story_info.get('is_ongoing', False)).lower(),
            previous_date=story_info.get('previous_date', ''),
            previous_date_json=previous_date_json
        )
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 4096,  # Enough for one story
                }
            )
            
            # Extract JSON
            response_text = None
            try:
                response_text = response.text
            except ValueError:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            response_text = ''.join(text_parts)
            
            if not response_text:
                raise ValueError("Could not extract text from Gemini response")
            
            # Extract and parse JSON
            json_text = extract_and_repair_json(response_text)
            story = json.loads(json_text)
            
            return story
            
        except Exception as e:
            logger.error(f"Error generating story {story_info.get('story_id')}: {e}")
            # Return a minimal story structure
            return {
                'title_hu': story_info.get('title_hu', 'Hiba történt'),
                'title_en': story_info.get('title_en', 'Error occurred'),
                'summary_hu': 'A történet generálása során hiba történt.',
                'summary_en': 'An error occurred while generating this story.',
                'sources_analyzed': [],
                'perspective_comparison': '',
                'key_facts': [],
                'is_ongoing': story_info.get('is_ongoing', False),
                'previous_date': story_info.get('previous_date')
            }
    
    def synthesize(self, categorized_articles, retry_count=3, include_previous_days=True):
        """
        Use Gemini to synthesize news from multiple perspectives using a two-step approach:
        1. First identify which stories to cover
        2. Then generate each story individually
        
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
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        stories = []
        
        # Step 1: Identify which stories to cover
        logger.info("Step 1: Identifying stories to cover...")
        for attempt in range(retry_count):
            try:
                max_stories = 3 if attempt == 0 else 2  # Start with 3, reduce to 2 on retry
                story_list = self.identify_stories(categorized_articles, previous_stories, max_stories)
                
                if story_list:
                    logger.info(f"Identified {len(story_list)} stories to cover")
                    break
                else:
                    if attempt < retry_count - 1:
                        logger.warning("No stories identified, retrying...")
                        continue
                    else:
                        # Fallback: create a default story
                        logger.warning("Could not identify stories, creating default story")
                        story_list = [{
                            'story_id': 1,
                            'title_hu': 'Fontos hírek',
                            'title_en': 'Important news',
                            'is_ongoing': False,
                            'previous_date': None
                        }]
            except Exception as e:
                logger.error(f"Error identifying stories (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    continue
                else:
                    # Fallback: create a default story
                    story_list = [{
                        'story_id': 1,
                        'title_hu': 'Fontos hírek',
                        'title_en': 'Important news',
                        'is_ongoing': False,
                        'previous_date': None
                    }]
        
        # Step 2: Generate each story individually
        logger.info(f"Step 2: Generating {len(story_list)} stories individually...")
        for i, story_info in enumerate(story_list, 1):
            logger.info(f"Generating story {i}/{len(story_list)}: {story_info.get('title_hu', 'Unknown')}")
            try:
                story = self.generate_single_story(story_info, categorized_articles, previous_stories)
                stories.append(story)
                logger.info(f"Successfully generated story {i}")
            except Exception as e:
                logger.error(f"Error generating story {i}: {e}")
                # Add a minimal story to continue
                stories.append({
                    'title_hu': story_info.get('title_hu', 'Hiba történt'),
                    'title_en': story_info.get('title_en', 'Error occurred'),
                    'summary_hu': 'A történet generálása során hiba történt.',
                    'summary_en': 'An error occurred while generating this story.',
                    'sources_analyzed': [],
                    'perspective_comparison': '',
                    'key_facts': [],
                    'is_ongoing': story_info.get('is_ongoing', False),
                    'previous_date': story_info.get('previous_date')
                })
        
        # Build final synthesis
        synthesis = {
            'date': date_str,
            'stories': stories,
            'methodology_note_hu': 'Automatikusan generálva több lépésben: először történetek azonosítása, majd egyenkénti generálás.',
            'methodology_note_en': 'Automatically generated in multiple steps: first story identification, then individual generation.',
            'metadata': {
                'sources_scraped': sum(len(articles) for articles in categorized_articles.values()),
                'generation_time': datetime.now().isoformat(),
                'ai_model': 'gemini-2.5-flash',
                'generation_method': 'two-step'
            }
        }
        
        logger.info(f"Successfully synthesized {len(stories)} stories using two-step approach")
        
        return synthesis
    
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

