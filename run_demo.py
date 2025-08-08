#!/usr/bin/env python3
"""StoryGenome Demo Runner"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fail {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import openai
        import sentence_transformers
        import plotly
        import pandas
        print("Success")
        return True
    except ImportError as e:
        print(f"Fail {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Fail: .env file not found")
        return False
    else:
        print("Success")
        return True

def main():
    """Main demo runner"""
    
    # Check dependencies
    if not check_dependencies():
        print("Fail: Dependencies check failed")
        return
    
    # Check environment
    if not check_env_file():
        print("Fail: Environment check failed")
        return
    
    # Create demo data
    if not run_command("python data/create_demo_data.py", "Creating demo data"):
        print("Fail: Demo data creation failed")
        return
    
    # Launch Streamlit app
    try:
        subprocess.run("streamlit run app/StoryGenome_app.py", shell=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass

if __name__ == "__main__":
    main()
