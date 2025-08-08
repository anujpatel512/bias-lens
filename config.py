"""Configuration settings for StoryGenome"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///story_genome.db")

# App Settings
SCORING_CACHE_TTL = int(os.getenv("SCORING_CACHE_TTL", "86400"))  # 24 hours
INGESTION_INTERVAL = int(os.getenv("INGESTION_INTERVAL", "1800"))  # 30 minutes
MAX_ARTICLES_PER_BATCH = int(os.getenv("MAX_ARTICLES_PER_BATCH", "50"))

# News Sources
NEWS_SOURCES = [
    "reuters", "associated-press", "bbc-news", "cnn", "fox-news", 
    "the-new-york-times", "the-washington-post", "the-guardian-uk",
    "the-wall-street-journal", "npr", "abc-news", "cbs-news",
    "msnbc", "politico", "axios", "the-hill"
]

# Bias Dimensions
BIAS_DIMENSIONS = {
    "framing": "Angle, causal attributions, villains/heroes",
    "omission": "Missing key facts, perspectives", 
    "tone": "Emotive vs neutral language",
    "source_selection": "Quoted/relied-on voices",
    "word_choice": "Loaded or euphemistic terms"
}

# Clustering
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
MIN_CLUSTER_SIZE = 3
MIN_SAMPLES = 2

# UI
APP_TITLE = "StoryGenome - News Bias Analysis"
APP_DESCRIPTION = "See how the same event is told differently across news outlets"
