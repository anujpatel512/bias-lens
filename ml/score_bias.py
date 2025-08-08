"""LLM-based bias scoring system with caching"""
import openai
import json
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY, BIAS_DIMENSIONS
from database import StoryGenomeDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiasScorer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.db = StoryGenomeDB()
        self.prompt_template = self._load_prompt_template()
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def _load_prompt_template(self) -> str:
        """Load the bias analysis prompt template"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts", "bias_prompt.md"
        )
        
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Prompt template not found, using default")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Fallback prompt template"""
        return """You are an expert media bias analyst. Analyze the article for bias across 5 dimensions:

1. Framing: How the story is presented - angle, causal attributions, villains/heroes
2. Omission: Missing key facts, perspectives, or context  
3. Tone: Emotive vs neutral language, sensationalism
4. Source Selection: Which voices are quoted/relied on, diversity of perspectives
5. Word Choice: Loaded terms, euphemisms, or biased language

Score each dimension 1-5 (1=minimal bias, 5=extreme bias).

Return ONLY valid JSON:
{
  "scores": {"framing": 1-5, "omission": 1-5, "tone": 1-5, "source_selection": 1-5, "word_choice": 1-5},
  "justifications": {"framing": "explanation", "omission": "explanation", "tone": "explanation", "source_selection": "explanation", "word_choice": "explanation"},
  "bias_phrases": [{"text": "phrase", "dimension": "dimension_name"}],
  "notable_claims": [{"span": "text", "claim": "description"}]
}

Title: {title}
Content: {content}"""
    
    def _truncate_text(self, text: str, max_tokens: int = 4000) -> str:
        """Truncate text to fit within token limits"""
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate to max_chars and try to end at a sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        end_pos = max(last_period, last_exclamation, last_question)
        if end_pos > max_chars * 0.8:  # If we can find a good break point
            return truncated[:end_pos + 1]
        
        return truncated + "..."
    
    def _generate_cache_key(self, title: str, content: str) -> str:
        """Generate cache key for article content"""
        text_hash = hashlib.md5(f"{title}:{content}".encode()).hexdigest()
        return f"bias_score_{text_hash}"
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if bias scores are cached"""
        # For MVP, we'll use a simple file-based cache
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    logger.info(f"Cache hit for {cache_key}")
                    return cached_data
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save bias scores to cache"""
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def score_article(self, title: str, content: str) -> Dict[str, Any]:
        """Score a single article for bias"""
        # Check cache first
        cache_key = self._generate_cache_key(title, content)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Truncate content to fit within token limits
        truncated_content = self._truncate_text(content)
        
        # Prepare prompt
        prompt = self.prompt_template.format(
            title=title,
            content=truncated_content
        )
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert media bias analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=2000
            )
            

            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Remove any markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text.strip())
                
                # Validate result structure
                required_keys = ["scores", "justifications", "bias_phrases", "notable_claims"]
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in response")
                
                # Validate scores
                score_keys = ["framing", "omission", "tone", "source_selection", "word_choice"]
                if not all(key in result["scores"] for key in score_keys):
                    raise ValueError("Missing bias dimension scores")
                
                # Cache the result
                self._save_to_cache(cache_key, result)
                
                logger.info(f"Successfully scored article: {title[:50]}...")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response: {response_text}")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._get_fallback_result()
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Return neutral fallback result when scoring fails"""
        return {
            "scores": {
                "framing": 3,
                "omission": 3,
                "tone": 3,
                "source_selection": 3,
                "word_choice": 3
            },
            "justifications": {
                "framing": "Unable to analyze framing bias due to processing error.",
                "omission": "Unable to analyze omission bias due to processing error.",
                "tone": "Unable to analyze tone bias due to processing error.",
                "source_selection": "Unable to analyze source selection bias due to processing error.",
                "word_choice": "Unable to analyze word choice bias due to processing error."
            },
            "bias_phrases": [],
            "notable_claims": []
        }
    
    def score_batch(self, articles: List[Dict]) -> int:
        """Score a batch of articles"""
        scored_count = 0
        
        for article in articles:
            try:
                # Score the article
                result = self.score_article(article['title'], article['text'])
                
                # Store scores in database
                self.db.insert_bias_scores(
                    article_id=article['id'],
                    scores=result['scores'],
                    justifications=result['justifications']
                )
                
                # Store bias phrases
                if result.get('bias_phrases'):
                    self.db.insert_bias_phrases(
                        article_id=article['id'],
                        phrases=result['bias_phrases']
                    )
                
                scored_count += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error scoring article {article.get('id')}: {e}")
                continue
        
        return scored_count
    
    def run_scoring(self, batch_size: int = 10):
        """Run bias scoring on articles that haven't been scored yet"""
        logger.info("Starting bias scoring...")
        
        # Get articles without scores
        articles = self.db.get_articles_without_scores(limit=batch_size)
        
        if not articles:
            logger.info("No articles found that need scoring")
            return 0
        
        logger.info(f"Found {len(articles)} articles to score")
        
        # Score articles in batches
        scored_count = self.score_batch(articles)
        
        logger.info(f"Scoring complete: {scored_count} articles scored")
        return scored_count

def main():
    """Main function for running bias scoring"""
    scorer = BiasScorer()
    scorer.run_scoring(batch_size=5)  # Start with small batch for demo

if __name__ == "__main__":
    main()
