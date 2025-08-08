"""Claim extraction and source linking system"""
import re
import logging
import requests
from typing import List, Dict, Any, Optional
import sys
import os
from urllib.parse import urlparse
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import StoryGenomeDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaimsLinker:
    def __init__(self):
        self.db = StoryGenomeDB()
        
        # Trusted domains for primary sources
        self.trusted_domains = {
            'gov', 'mil', 'edu', 'org',
            'whitehouse.gov', 'congress.gov', 'supremecourt.gov',
            'who.int', 'un.org', 'europa.eu'
        }
        
        # Common claim patterns
        self.claim_patterns = [
            r'(\w+\s+said\s+[^.]*\.)',  # "X said..."
            r'(\w+\s+announced\s+[^.]*\.)',  # "X announced..."
            r'(\w+\s+reported\s+[^.]*\.)',  # "X reported..."
            r'(\w+\s+found\s+[^.]*\.)',  # "X found..."
            r'(\w+\s+study\s+[^.]*\.)',  # "X study..."
            r'(\w+\s+research\s+[^.]*\.)',  # "X research..."
            r'(\w+\s+data\s+[^.]*\.)',  # "X data..."
            r'(\w+\s+statistics\s+[^.]*\.)',  # "X statistics..."
        ]
    
    def extract_claims(self, text: str) -> List[Dict[str, str]]:
        """Extract potential claims from article text"""
        claims = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Check for claim patterns
            for pattern in self.claim_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    span_text = match.group(1)
                    
                    # Extract potential entities (names, organizations)
                    entities = self._extract_entities(span_text)
                    
                    claims.append({
                        'span': span_text,
                        'claim': self._summarize_claim(span_text),
                        'entities': entities
                    })
        
        return claims[:10]  # Limit to top 10 claims
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential named entities from text"""
        entities = []
        
        # Look for capitalized words (potential names/organizations)
        words = text.split()
        for i, word in enumerate(words):
            if (word[0].isupper() and len(word) > 2 and 
                not word.lower() in ['the', 'and', 'but', 'for', 'with', 'this', 'that']):
                
                # Check if it's part of a multi-word entity
                entity = word
                if i > 0 and words[i-1][0].isupper():
                    entity = words[i-1] + " " + entity
                
                entities.append(entity)
        
        return list(set(entities))  # Remove duplicates
    
    def _summarize_claim(self, text: str) -> str:
        """Create a brief summary of the claim"""
        # Remove common reporting verbs
        text = re.sub(r'\b(said|announced|reported|found|study|research|data|statistics)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if len(text) > 100:
            text = text[:97] + "..."
        
        return text
    
    def search_primary_sources(self, claim: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search for primary sources to verify a claim"""
        # For MVP, we'll do a simple web search simulation
        # In a full implementation, this would use a search API
        
        entities = claim.get('entities', [])
        claim_text = claim.get('claim', '')
        
        # Simulate finding a source (in real implementation, this would be a web search)
        if entities and len(claim_text) > 10:
            # Check if any entities match trusted domains
            for entity in entities:
                entity_lower = entity.lower()
                for domain in self.trusted_domains:
                    if domain in entity_lower:
                        return {
                            'url': f"https://{domain}/relevant-page",
                            'confidence': 0.7,
                            'source_type': 'government',
                            'matched_entity': entity
                        }
        
        # Simulate finding a news source
        if any(word in claim_text.lower() for word in ['study', 'research', 'data', 'report']):
            return {
                'url': 'https://example-research-institute.org/study',
                'confidence': 0.5,
                'source_type': 'research',
                'matched_entity': 'research'
            }
        
        return None
    
    def process_article_claims(self, article_id: int, text: str):
        """Process claims for a single article"""
        try:
            # Extract claims
            claims = self.extract_claims(text)
            
            # For each claim, try to find primary sources
            for claim in claims:
                source_info = self.search_primary_sources(claim)
                
                # Store claim in database
                self.db.insert_claim(
                    article_id=article_id,
                    span=claim['span'],
                    entity=claim.get('entities', []),
                    claim_text=claim['claim'],
                    evidence_url=source_info.get('url') if source_info else None,
                    evidence_conf=source_info.get('confidence') if source_info else None
                )
            
            logger.info(f"Processed {len(claims)} claims for article {article_id}")
            
        except Exception as e:
            logger.error(f"Error processing claims for article {article_id}: {e}")
    
    def run_claims_processing(self, batch_size: int = 20):
        """Run claims processing on articles that haven't been processed yet"""
        logger.info("Starting claims processing...")
        
        # Get articles without claims
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT a.id, a.text
                FROM articles a
                LEFT JOIN claims c ON a.id = c.article_id
                WHERE c.id IS NULL
                ORDER BY a.published_at DESC
                LIMIT ?
            """, (batch_size,))
            
            articles = cursor.fetchall()
        
        if not articles:
            logger.info("No articles found that need claims processing")
            return 0
        
        processed_count = 0
        for article_id, text in articles:
            try:
                self.process_article_claims(article_id, text)
                processed_count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing article {article_id}: {e}")
                continue
        
        logger.info(f"Claims processing complete: {processed_count} articles processed")
        return processed_count

def main():
    """Main function for running claims processing"""
    linker = ClaimsLinker()
    linker.run_claims_processing(batch_size=10)

if __name__ == "__main__":
    main()
