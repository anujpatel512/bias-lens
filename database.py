"""Database schema and connection management for StoryGenome"""
import sqlite3
import json
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoryGenomeDB:
    def __init__(self, db_path: str = "story_genome.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    outlet TEXT NOT NULL,
                    author TEXT,
                    published_at TIMESTAMP,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS bias_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    framing REAL,
                    omission REAL,
                    tone REAL,
                    source_selection REAL,
                    word_choice REAL,
                    justification_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                );
                
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    vector BLOB,
                    model_name TEXT DEFAULT 'all-mpnet-base-v2',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                );
                
                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id INTEGER PRIMARY KEY,
                    label TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS cluster_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id INTEGER NOT NULL,
                    article_id INTEGER NOT NULL,
                    distance_to_center REAL,
                    FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id),
                    FOREIGN KEY (article_id) REFERENCES articles (id),
                    UNIQUE(cluster_id, article_id)
                );
                
                CREATE TABLE IF NOT EXISTS bias_phrases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    phrase TEXT NOT NULL,
                    dimension TEXT NOT NULL,
                    start_idx INTEGER,
                    end_idx INTEGER,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                );
                
                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    span TEXT NOT NULL,
                    entity TEXT,
                    claim_text TEXT NOT NULL,
                    evidence_url TEXT,
                    evidence_conf REAL,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_articles_outlet ON articles(outlet);
                CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
                CREATE INDEX IF NOT EXISTS idx_bias_scores_article ON bias_scores(article_id);
                CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON cluster_members(cluster_id);
                CREATE INDEX IF NOT EXISTS idx_cluster_members_article ON cluster_members(article_id);
            """)
            logger.info("Database initialized successfully")
    
    def insert_article(self, url: str, outlet: str, title: str, text: str, 
                      author: str = None, published_at: datetime = None) -> int:
        """Insert new article and return article_id"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO articles (url, outlet, author, published_at, title, text)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, outlet, author, published_at, title, text))
            return cursor.lastrowid
    
    def insert_bias_scores(self, article_id: int, scores: Dict[str, float], 
                          justifications: Dict[str, str]):
        """Insert bias scores for an article"""
        justification_json = json.dumps(justifications)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO bias_scores 
                (article_id, framing, omission, tone, source_selection, word_choice, justification_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (article_id, scores['framing'], scores['omission'], scores['tone'],
                  scores['source_selection'], scores['word_choice'], justification_json))
    
    def insert_embedding(self, article_id: int, vector: List[float], model_name: str):
        """Insert embedding vector for an article"""
        vector_blob = pickle.dumps(vector)
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO embeddings (article_id, vector, model_name)
                VALUES (?, ?, ?)
            """, (article_id, vector_blob, model_name))
    
    def insert_bias_phrases(self, article_id: int, phrases: List[Dict]):
        """Insert bias phrases for an article"""
        with self.get_connection() as conn:
            for phrase in phrases:
                conn.execute("""
                    INSERT INTO bias_phrases (article_id, phrase, dimension, start_idx, end_idx)
                    VALUES (?, ?, ?, ?, ?)
                """, (article_id, phrase['text'], phrase['dimension'], 
                      phrase.get('start_idx'), phrase.get('end_idx')))
    
    def get_articles_without_scores(self, limit: int = 50) -> List[Dict]:
        """Get articles that haven't been scored yet"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT a.id, a.url, a.outlet, a.title, a.text, a.published_at
                FROM articles a
                LEFT JOIN bias_scores bs ON a.id = bs.article_id
                WHERE bs.id IS NULL
                ORDER BY a.published_at DESC
                LIMIT ?
            """, (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_articles_without_embeddings(self, limit: int = 50) -> List[Dict]:
        """Get articles that haven't been embedded yet"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT a.id, a.title, a.text
                FROM articles a
                LEFT JOIN embeddings e ON a.id = e.article_id
                WHERE e.id IS NULL
                LIMIT ?
            """, (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_all_embeddings(self) -> List[Dict]:
        """Get all article embeddings for clustering"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT e.article_id, e.vector, a.title, a.outlet, a.published_at
                FROM embeddings e
                JOIN articles a ON e.article_id = a.id
                ORDER BY a.published_at DESC
            """)
            results = []
            for row in cursor.fetchall():
                results.append({
                    'article_id': row[0],
                    'vector': pickle.loads(row[1]),
                    'title': row[2],
                    'outlet': row[3],
                    'published_at': row[4]
                })
            return results
    
    def update_clusters(self, cluster_assignments: Dict[int, int], cluster_labels: Dict[int, str]):
        """Update cluster assignments and labels"""
        with self.get_connection() as conn:
            # Clear existing cluster data
            conn.execute("DELETE FROM cluster_members")
            conn.execute("DELETE FROM clusters")
            
            # Insert new clusters
            for cluster_id, label in cluster_labels.items():
                conn.execute("""
                    INSERT INTO clusters (cluster_id, label)
                    VALUES (?, ?)
                """, (cluster_id, label))
            
            # Insert cluster memberships
            for article_id, cluster_id in cluster_assignments.items():
                if cluster_id >= 0:  # -1 indicates noise/outlier
                    conn.execute("""
                        INSERT INTO cluster_members (cluster_id, article_id)
                        VALUES (?, ?)
                    """, (cluster_id, article_id))
    
    def get_clusters_with_articles(self) -> List[Dict]:
        """Get all clusters with their articles"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    c.cluster_id, c.label, c.created_at,
                    COUNT(cm.article_id) as article_count,
                    GROUP_CONCAT(DISTINCT a.outlet) as outlets
                FROM clusters c
                LEFT JOIN cluster_members cm ON c.cluster_id = cm.cluster_id
                LEFT JOIN articles a ON cm.article_id = a.id
                GROUP BY c.cluster_id, c.label, c.created_at
                ORDER BY c.created_at DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_cluster_articles(self, cluster_id: int) -> List[Dict]:
        """Get all articles in a specific cluster with bias scores"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    a.id, a.url, a.outlet, a.title, a.text, a.published_at,
                    bs.framing, bs.omission, bs.tone, bs.source_selection, bs.word_choice,
                    bs.justification_json
                FROM cluster_members cm
                JOIN articles a ON cm.article_id = a.id
                LEFT JOIN bias_scores bs ON a.id = bs.article_id
                WHERE cm.cluster_id = ?
                ORDER BY a.published_at DESC
            """, (cluster_id,))
            columns = [desc[0] for desc in cursor.description]
            articles = []
            for row in cursor.fetchall():
                article = dict(zip(columns, row))
                if article['justification_json']:
                    article['justifications'] = json.loads(article['justification_json'])
                articles.append(article)
            return articles
    
    def get_article_phrases(self, article_id: int) -> List[Dict]:
        """Get bias phrases for an article"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT phrase, dimension, start_idx, end_idx
                FROM bias_phrases
                WHERE article_id = ?
            """, (article_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def insert_claim(self, article_id: int, span: str, entity: str, claim_text: str, 
                    evidence_url: str = None, evidence_conf: float = None):
        """Insert a claim for an article"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO claims (article_id, span, entity, claim_text, evidence_url, evidence_conf)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (article_id, span, entity, claim_text, evidence_url, evidence_conf))
    
    def article_exists(self, url: str) -> bool:
        """Check if article already exists"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    
    def insert_claim(self, article_id: int, span: str, entity: str, claim_text: str, 
                    evidence_url: str = None, evidence_conf: float = None):
        """Insert a claim for an article"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO claims (article_id, span, entity, claim_text, evidence_url, evidence_conf)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (article_id, span, entity, claim_text, evidence_url, evidence_conf))