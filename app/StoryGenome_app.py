"""StoryGenome Streamlit UI Application"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_TITLE, APP_DESCRIPTION, BIAS_DIMENSIONS
from database import StoryGenomeDB

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_db():
    return StoryGenomeDB()

db = get_db()

def create_bias_radar_chart(scores: dict, title: str = "Bias Analysis"):
    """Create a radar chart for bias scores"""
    dimensions = list(BIAS_DIMENSIONS.keys())
    values = [scores.get(dim, 0) for dim in dimensions]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=dimensions,
        fill='toself',
        name=title,
        line_color='rgb(32, 201, 151)',
        fillcolor='rgba(32, 201, 151, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title=title,
        height=400
    )
    
    return fig

def create_comparison_radar_chart(articles_data: list):
    """Create a comparison radar chart for multiple articles"""
    dimensions = list(BIAS_DIMENSIONS.keys())
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, article in enumerate(articles_data):
        outlet = article['outlet']
        scores = {
            'framing': article.get('framing', 0),
            'omission': article.get('omission', 0),
            'tone': article.get('tone', 0),
            'source_selection': article.get('source_selection', 0),
            'word_choice': article.get('word_choice', 0)
        }
        
        values = [scores.get(dim, 0) for dim in dimensions]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=dimensions,
            fill='toself',
            name=outlet,
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.3)')
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title="Bias Comparison Across Outlets",
        height=500
    )
    
    return fig

def highlight_bias_phrases(text: str, phrases: list) -> str:
    """Highlight bias phrases in text with HTML markup"""
    if not phrases:
        return text
    
    highlighted_text = text
    
    # Sort phrases by length (longest first) to avoid partial matches
    # Database returns 'phrase' key, not 'text'
    sorted_phrases = sorted(phrases, key=lambda x: len(x.get('phrase', x.get('text', ''))), reverse=True)
    
    for phrase in sorted_phrases:
        # Handle both 'phrase' (from database) and 'text' (from demo data) keys
        phrase_text = phrase.get('phrase', phrase.get('text', ''))
        dimension = phrase.get('dimension', 'unknown')
        
        # Create color-coded highlight based on dimension
        colors = {
            'framing': '#FF6B6B',
            'omission': '#4ECDC4',
            'tone': '#45B7D1',
            'source_selection': '#96CEB4',
            'word_choice': '#FFEAA7'
        }
        
        color = colors.get(dimension, '#FF6B6B')
        
        # Replace phrase with highlighted version
        highlighted_text = highlighted_text.replace(
            phrase_text,
            f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" title="{dimension}">{phrase_text}</mark>'
        )
    
    return highlighted_text

def main():
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    
    # Sidebar
    st.sidebar.header("Navigation")
    
    # Get clusters
    clusters = db.get_clusters_with_articles()
    
    if not clusters:
        st.warning("No clusters found. Please run the ingestion and clustering pipeline first.")
        st.info("Run the following commands in order:")
        st.code("""
        python ingest/fetch_news.py
        python ml/score_bias.py
        python ml/cluster.py
        """)
        return
    
    # Cluster selection
    cluster_options = [c['cluster_id'] for c in clusters]
    cluster_labels = {c['cluster_id']: f"{c['label']} ({c['article_count']} articles)" for c in clusters}
    
    selected_cluster = st.sidebar.selectbox(
        "Select a Story Cluster",
        options=cluster_options,
        format_func=lambda x: cluster_labels[x]
    )
    
    if selected_cluster:
        # Get articles in selected cluster
        articles = db.get_cluster_articles(selected_cluster)
        
        if not articles:
            st.error("No articles found in this cluster.")
            return
        
        # Display cluster info
        cluster_info = next(c for c in clusters if c['cluster_id'] == selected_cluster)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Articles", cluster_info['article_count'])
        with col2:
            st.metric("Outlets", len(set(a['outlet'] for a in articles)))
        with col3:
            # Handle published_at which might be a string or datetime
            latest_date = max(a['published_at'] for a in articles if a['published_at'])
            if hasattr(latest_date, 'strftime'):
                latest_str = latest_date.strftime('%m/%d')
            else:
                # If it's a string, try to parse it or just show as is
                latest_str = str(latest_date)[:10] if latest_date else "N/A"
            st.metric("Latest", latest_str)
        
        st.subheader(f"📰 {cluster_info['label']}")
        
        # Outlet comparison
        st.header("📊 Outlet Comparison")
        
        # Create comparison chart
        comparison_fig = create_comparison_radar_chart(articles)
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        # Outlet selection for detailed view
        st.header("📖 Article Analysis")
        
        outlets = list(set(a['outlet'] for a in articles))
        selected_outlet = st.selectbox("Select an outlet to analyze:", outlets)
        
        # Filter articles by selected outlet
        outlet_articles = [a for a in articles if a['outlet'] == selected_outlet]
        
        if outlet_articles:
            selected_article = st.selectbox(
                "Select an article:",
                outlet_articles,
                format_func=lambda x: f"{x['title'][:80]}..."
            )
            
            if selected_article:
                # Display article details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(selected_article['title'])
                    # Format the published date safely
                    pub_date = selected_article['published_at']
                    if hasattr(pub_date, 'strftime'):
                        date_str = pub_date.strftime('%Y-%m-%d %H:%M')
                    else:
                        date_str = str(pub_date) if pub_date else "Unknown date"
                    st.caption(f"By {selected_article.get('author', 'Unknown')} | {selected_article['outlet']} | {date_str}")
                    
                    # Display article text with bias highlights
                    phrases = db.get_article_phrases(selected_article['id'])
                    highlighted_text = highlight_bias_phrases(selected_article['text'], phrases)
                    
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                    
                    if selected_article['url']:
                        st.markdown(f"[Read full article]({selected_article['url']})")
                
                with col2:
                    # Bias radar chart
                    scores = {
                        'framing': selected_article.get('framing', 0),
                        'omission': selected_article.get('omission', 0),
                        'tone': selected_article.get('tone', 0),
                        'source_selection': selected_article.get('source_selection', 0),
                        'word_choice': selected_article.get('word_choice', 0)
                    }
                    
                    radar_fig = create_bias_radar_chart(scores, f"{selected_article['outlet']} Bias Analysis")
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    # Bias justifications
                    if selected_article.get('justifications'):
                        st.subheader("Bias Analysis")
                        for dimension, justification in selected_article['justifications'].items():
                            st.markdown(f"**{dimension.title()}:** {justification}")
                
                # Claims and sources
                st.header("🔍 Claims & Sources")
                
                with db.get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT span, claim_text, evidence_url, evidence_conf
                        FROM claims
                        WHERE article_id = ?
                    """, (selected_article['id'],))
                    
                    claims = cursor.fetchall()
                
                if claims:
                    for span, claim_text, evidence_url, evidence_conf in claims:
                        with st.expander(f"Claim: {claim_text[:100]}..."):
                            st.write(f"**Original text:** {span}")
                            st.write(f"**Claim:** {claim_text}")
                            
                            if evidence_url:
                                confidence_color = "green" if evidence_conf > 0.7 else "orange" if evidence_conf > 0.4 else "red"
                                st.markdown(f"**Source:** [{evidence_url}]({evidence_url})")
                                st.markdown(f"**Confidence:** :{confidence_color}[{evidence_conf:.1%}]")
                            else:
                                st.warning("No primary source found")
                else:
                    st.info("No claims extracted from this article.")
        
        # Dimension comparison across outlets
        st.header("📈 Dimension Comparison")
        
        # Create dimension comparison chart
        dimension_data = []
        for article in articles:
            dimension_data.append({
                'outlet': article['outlet'],
                'dimension': 'framing',
                'score': article.get('framing', 0)
            })
            dimension_data.append({
                'outlet': article['outlet'],
                'dimension': 'omission',
                'score': article.get('omission', 0)
            })
            dimension_data.append({
                'outlet': article['outlet'],
                'dimension': 'tone',
                'score': article.get('tone', 0)
            })
            dimension_data.append({
                'outlet': article['outlet'],
                'dimension': 'source_selection',
                'score': article.get('source_selection', 0)
            })
            dimension_data.append({
                'outlet': article['outlet'],
                'dimension': 'word_choice',
                'score': article.get('word_choice', 0)
            })
        
        if dimension_data:
            df = pd.DataFrame(dimension_data)
            
            fig = px.box(df, x='dimension', y='score', color='outlet',
                        title="Bias Score Distribution by Dimension and Outlet")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>StoryGenome - See how the same event is told differently across news outlets</p>
        <p>Built with Streamlit, OpenAI, and HDBSCAN</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
