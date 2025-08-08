# StoryGenome - News Bias Analysis

See how the same event is told differently across news outlets, highlighting language divergence, bias dimensions, and (un)sourced claims.

## Quick Start

### Option 1: Demo Mode (No API Keys Required)

Run the demo with sample data:
```
python run_demo.py
```

This will:
- Create sample AI regulation articles
- Launch the app at http://localhost:8501
- Show bias analysis across 5 news outlets

### Option 2: Real News Mode (Requires API Keys)

1. Create .env file with your API keys:
```
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "NEWS_API_KEY=your_news_api_key_here" >> .env
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Fetch real news articles:
```
python ingest/fetch_news.py
```

4. Analyze bias:
```
python ml/score_bias.py
```

5. Cluster articles:
```
python ml/cluster.py
```

6. Launch app:
```
streamlit run app/StoryGenome_app.py
```

## What You'll See

- Bias Radar Charts: Compare outlets across 5 dimensions (framing, omission, tone, source selection, word choice)
- Article Comparison: Side-by-side analysis of the same story
- Highlighted Phrases: Bias indicators highlighted in article text
- Narrative Clustering: Articles grouped by similar stories

## API Keys Needed

- OpenAI API Key: For bias analysis (GPT-4)
- News API Key: For fetching articles (free tier available at newsapi.org)

## Demo Data

The demo includes 5 AI regulation articles from:
- CNN, Fox News, Reuters, The New York Times, The Wall Street Journal

Each article has pre-analyzed bias scores and highlighted phrases.

## Deploy to Streamlit Cloud

Want to share your app with others? Deploy it to Streamlit Cloud for free!

1. **Push your code to GitHub**
2. **Visit [Streamlit Cloud](https://share.streamlit.io/)**
3. **Connect your repository and deploy**
4. **Add your API keys as secrets**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Your app will be available at: `https://your-app-name-your-username.streamlit.app`
