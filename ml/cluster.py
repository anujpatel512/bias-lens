"""Article clustering using embeddings and HDBSCAN"""
import numpy as np
import logging
from typing import List, Dict, Any, Tuple
import sys
import os
from datetime import datetime
import re
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler
import hdbscan

from config import EMBEDDING_MODEL, MIN_CLUSTER_SIZE, MIN_SAMPLES
from database import StoryGenomeDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleClusterer:
    def __init__(self):
        self.db = StoryGenomeDB()
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2
        )
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess article text for clustering"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Keep only alphanumeric, spaces, and basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        return text.lower()
    
    def generate_embeddings(self, articles: List[Dict]) -> Tuple[List[int], np.ndarray]:
        """Generate embeddings for articles"""
        article_ids = []
        texts = []
        
        for article in articles:
            # Combine title and first few paragraphs for embedding
            title = article.get('title', '')
            text = article.get('text', '')
            
            # Take first 1000 characters of text
            text_preview = text[:1000] if text else ""
            
            combined_text = f"{title}. {text_preview}"
            processed_text = self.preprocess_text(combined_text)
            
            if len(processed_text) > 50:  # Only include if we have substantial text
                article_ids.append(article['id'])
                texts.append(processed_text)
        
        if not texts:
            logger.warning("No valid texts found for embedding")
            return [], np.array([])
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} articles...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        return article_ids, embeddings
    
    def store_embeddings(self, article_ids: List[int], embeddings: np.ndarray):
        """Store embeddings in database"""
        for article_id, embedding in zip(article_ids, embeddings):
            try:
                self.db.insert_embedding(
                    article_id=article_id,
                    vector=embedding.tolist(),
                    model_name=EMBEDDING_MODEL
                )
            except Exception as e:
                logger.error(f"Error storing embedding for article {article_id}: {e}")
    
    def cluster_articles(self, embeddings: np.ndarray) -> np.ndarray:
        """Cluster articles using HDBSCAN"""
        if len(embeddings) < MIN_CLUSTER_SIZE:
            logger.warning(f"Not enough articles for clustering (need at least {MIN_CLUSTER_SIZE})")
            return np.array([-1] * len(embeddings))  # All noise
        
        # Standardize embeddings
        scaler = StandardScaler()
        embeddings_scaled = scaler.fit_transform(embeddings)
        
        # Apply HDBSCAN clustering
        clusterer = HDBSCAN(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        cluster_labels = clusterer.fit_predict(embeddings_scaled)
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        logger.info(f"Clustering complete: {n_clusters} clusters, {n_noise} noise points")
        
        return cluster_labels
    
    def generate_cluster_labels(self, articles: List[Dict], cluster_labels: np.ndarray) -> Dict[int, str]:
        """Generate descriptive labels for clusters using TF-IDF"""
        cluster_labels_dict = {}
        
        # Group articles by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label >= 0:  # Skip noise points
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(articles[i])
        
        # Generate labels for each cluster
        for cluster_id, cluster_articles in clusters.items():
            # Combine all texts in the cluster
            texts = []
            for article in cluster_articles:
                title = article.get('title', '')
                text = article.get('text', '')
                combined = f"{title} {text[:500]}"  # Use title + first 500 chars
                texts.append(self.preprocess_text(combined))
            
            if not texts:
                cluster_labels_dict[cluster_id] = f"Cluster {cluster_id}"
                continue
            
            # Fit TF-IDF on cluster texts
            try:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                
                # Get top terms
                tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
                top_indices = tfidf_sums.argsort()[-5:][::-1]  # Top 5 terms
                top_terms = [feature_names[i] for i in top_indices if tfidf_sums[i] > 0]
                
                # Create label from top terms
                if top_terms:
                    label = " ".join(top_terms[:3])  # Use top 3 terms
                    label = label.replace('_', ' ').title()
                else:
                    label = f"Cluster {cluster_id}"
                
                cluster_labels_dict[cluster_id] = label
                
            except Exception as e:
                logger.error(f"Error generating label for cluster {cluster_id}: {e}")
                cluster_labels_dict[cluster_id] = f"Cluster {cluster_id}"
        
        return cluster_labels_dict
    
    def run_clustering(self):
        """Run the complete clustering pipeline"""
        logger.info("Starting article clustering...")
        
        # Get articles with embeddings but no cluster assignment
        articles_data = self.db.get_all_embeddings()
        
        if not articles_data:
            logger.info("No articles with embeddings found")
            return 0
        
        # Extract data
        article_ids = [item['article_id'] for item in articles_data]
        embeddings = np.array([item['vector'] for item in articles_data])
        
        # Check if we have enough articles
        if len(embeddings) < MIN_CLUSTER_SIZE:
            logger.info(f"Not enough articles for clustering (have {len(embeddings)}, need {MIN_CLUSTER_SIZE})")
            return 0
        
        # Perform clustering
        cluster_labels = self.cluster_articles(embeddings)
        
        # Generate cluster labels
        cluster_labels_dict = self.generate_cluster_labels(articles_data, cluster_labels)
        
        # Create cluster assignments mapping
        cluster_assignments = {}
        for article_id, label in zip(article_ids, cluster_labels):
            if label >= 0:  # Only include non-noise points
                cluster_assignments[article_id] = label
        
        # Update database with cluster information
        self.db.update_clusters(cluster_assignments, cluster_labels_dict)
        
        logger.info(f"Clustering complete: {len(cluster_labels_dict)} clusters created")
        return len(cluster_labels_dict)
    
    def generate_embeddings_for_unprocessed(self):
        """Generate embeddings for articles that don't have them yet"""
        logger.info("Generating embeddings for unprocessed articles...")
        
        # Get articles without embeddings
        articles = self.db.get_articles_without_embeddings(limit=50)
        
        if not articles:
            logger.info("No articles found that need embeddings")
            return 0
        
        # Generate embeddings
        article_ids, embeddings = self.generate_embeddings(articles)
        
        if not article_ids:
            logger.info("No valid articles for embedding generation")
            return 0
        
        # Store embeddings
        self.store_embeddings(article_ids, embeddings)
        
        logger.info(f"Generated embeddings for {len(article_ids)} articles")
        return len(article_ids)

def main():
    """Main function for running clustering"""
    clusterer = ArticleClusterer()
    
    # First generate embeddings for any unprocessed articles
    clusterer.generate_embeddings_for_unprocessed()
    
    # Then run clustering
    clusterer.run_clustering()

if __name__ == "__main__":
    main()
