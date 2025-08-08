# StoryGenome Deployment Guide

## Deploy to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at https://share.streamlit.io/)
3. Your code pushed to a GitHub repository

### Step 1: Prepare Your Repository

1. **Ensure your code is in a GitHub repository**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository root:**
   - `streamlit_app.py` (main entry point)
   - `requirements.txt` (Python dependencies)
   - `packages.txt` (system dependencies)
   - `.streamlit/config.toml` (Streamlit configuration)

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your GitHub repository
   - Set the main file path to: `streamlit_app.py`
   - Choose your branch (usually `main`)

3. **Configure Environment Variables**
   - In the app settings, add these secrets:
   ```
   OPENAI_API_KEY = your_openai_api_key_here
   NEWS_API_KEY = your_news_api_key_here
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait for the build to complete

### Step 3: Share Your App

Once deployed, you'll get a URL like:
```
https://your-app-name-your-username.streamlit.app
```

You can share this link with anyone!

## Environment Variables for Production

For the live deployment, you'll need to set these in Streamlit Cloud's secrets:

### Required for Real News Mode:
- `OPENAI_API_KEY`: Your OpenAI API key for bias analysis
- `NEWS_API_KEY`: Your News API key for fetching articles

### Optional:
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SCORING_CACHE_TTL`: Cache duration in seconds (default: 86400)
- `MAX_ARTICLES_PER_BATCH`: Max articles per batch (default: 50)

## Demo Mode vs Real News Mode

- **Demo Mode**: Works without API keys, uses pre-generated sample data
- **Real News Mode**: Requires API keys, fetches and analyzes real articles

## Troubleshooting

### Common Issues:

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **Import errors**: Ensure all Python files are in the correct directories
3. **API key errors**: Verify secrets are set correctly in Streamlit Cloud
4. **Database issues**: The app will create a new SQLite database on each deployment

### Performance Tips:

1. **Use caching**: The app already implements caching for bias scores
2. **Limit batch sizes**: Adjust `MAX_ARTICLES_PER_BATCH` for your needs
3. **Monitor API usage**: Track your OpenAI and News API usage

## Local Development vs Production

- **Local**: Uses `.env` file for environment variables
- **Production**: Uses Streamlit Cloud secrets for environment variables

The app automatically detects which environment it's running in and uses the appropriate configuration.
