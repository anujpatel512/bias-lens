#!/usr/bin/env python3
"""
StoryGenome - News Bias Analysis
Main entry point for Streamlit Cloud deployment
"""

import streamlit as st
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import and run the main app
from StoryGenome_app import main

if __name__ == "__main__":
    main()
