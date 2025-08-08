"""Create demo data for StoryGenome testing"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import StoryGenomeDB

def create_demo_articles():
    """Create sample articles for demo purposes"""
    db = StoryGenomeDB()
    
    # Sample articles about the same event (AI regulation)
    demo_articles = [
        {
            'url': 'https://example.com/cnn-ai-regulation',
            'outlet': 'CNN',
            'title': 'Biden Administration Takes Aggressive Stance on AI Regulation',
            'text': '''The Biden administration announced sweeping new regulations on artificial intelligence today, marking the most comprehensive attempt to rein in the rapidly developing technology. President Biden described the move as "essential for protecting American workers and consumers" from potential AI threats.

The new rules will require AI companies to submit their systems for government review before deployment, a move that industry leaders say could stifle innovation. "This is a heavy-handed approach that will put America behind in the global AI race," said tech industry spokesperson Sarah Johnson.

However, consumer advocates praised the regulations. "For too long, AI companies have operated without proper oversight," said consumer rights advocate Michael Chen. "These regulations are long overdue and will protect millions of Americans."

The regulations come amid growing concerns about AI's impact on jobs, privacy, and national security. Recent studies have shown that AI could displace millions of workers in the coming decade, while also raising serious privacy concerns.

Critics argue that the regulations are too broad and could harm small AI startups. "This is a classic case of government overreach," said libertarian think tank director Robert Smith. "The free market should be allowed to regulate itself."''',
            'author': 'Jennifer Martinez',
            'published_at': datetime.now() - timedelta(hours=2)
        },
        {
            'url': 'https://example.com/fox-ai-regulation',
            'outlet': 'Fox News',
            'title': 'Biden\'s AI Crackdown: Government Overreach or Necessary Protection?',
            'text': '''The Biden administration's new AI regulations represent yet another example of government overreach that threatens to stifle American innovation and economic growth. The sweeping new rules, announced today, will require AI companies to submit their systems for government approval before bringing them to market.

"This is a classic case of Democrats using regulation to control private industry," said conservative policy analyst David Wilson. "The free market has been driving AI innovation, and now the government wants to step in and slow everything down."

Industry leaders are warning that these regulations could put the United States at a competitive disadvantage. "China and other countries are moving full speed ahead with AI development while we're putting up bureaucratic roadblocks," said tech entrepreneur Lisa Rodriguez.

Supporters of the regulations argue they're necessary to protect consumers and workers. "AI technology is advancing so rapidly that we need some guardrails," said Democratic Senator Maria Garcia. "These regulations strike the right balance between innovation and protection."

However, critics point out that the regulations are vague and could be interpreted broadly. "This gives the government unprecedented power to control what AI systems can be developed and deployed," said constitutional law expert James Thompson. "It's a slippery slope toward more government control over technology."''',
            'author': 'Mark Johnson',
            'published_at': datetime.now() - timedelta(hours=1)
        },
        {
            'url': 'https://example.com/reuters-ai-regulation',
            'outlet': 'Reuters',
            'title': 'U.S. Announces New AI Regulations to Address Safety Concerns',
            'text': '''The United States government today announced new regulations governing artificial intelligence development and deployment. The rules, which will take effect in 90 days, establish a framework for AI safety and oversight.

The regulations require AI companies to conduct safety assessments and submit their systems for government review before commercial deployment. Companies must also implement safeguards to prevent AI systems from causing harm to users or society.

"These regulations represent a balanced approach to AI governance," said White House technology advisor Dr. Emily Chen. "We're protecting public safety while maintaining America's leadership in AI innovation."

Industry response has been mixed. Large technology companies generally support the framework, while smaller startups express concerns about compliance costs. "The regulations provide much-needed clarity for the industry," said TechCorp CEO Sarah Williams.

The new rules also establish an AI Safety Board to oversee implementation and provide guidance to companies. The board will include representatives from government, industry, and academia.

International observers note that the U.S. regulations are less restrictive than those recently implemented in the European Union, potentially giving American companies a competitive advantage in global markets.''',
            'author': 'Reuters Staff',
            'published_at': datetime.now() - timedelta(hours=3)
        },
        {
            'url': 'https://example.com/nyt-ai-regulation',
            'outlet': 'The New York Times',
            'title': 'Biden Administration Proposes Comprehensive AI Safety Framework',
            'text': '''The Biden administration unveiled a comprehensive framework for regulating artificial intelligence today, addressing growing concerns about the technology's potential risks while seeking to maintain American competitiveness in the global AI race.

The new regulations, developed over 18 months of consultation with industry leaders, academics, and civil society groups, establish mandatory safety standards for AI systems used in critical applications. Companies developing AI for healthcare, transportation, and financial services will face the strictest oversight.

"This framework represents a thoughtful approach to a complex challenge," said Dr. Rachel Green, director of the White House Office of Science and Technology Policy. "We're not trying to stop AI innovation, but we are ensuring it happens responsibly."

The regulations include provisions for transparency, requiring companies to disclose how their AI systems make decisions. They also establish mechanisms for ongoing monitoring and updates as AI technology evolves.

Industry leaders have largely welcomed the framework, though some express concerns about implementation timelines. "The government has listened to our concerns and created a workable framework," said AI Alliance spokesperson David Kim.

Consumer advocates praised the regulations for addressing privacy and bias concerns. "For the first time, we have meaningful protections against AI systems that could discriminate or violate privacy," said Consumer Watchdog director Lisa Park.''',
            'author': 'Thomas Anderson',
            'published_at': datetime.now() - timedelta(hours=4)
        },
        {
            'url': 'https://example.com/wsj-ai-regulation',
            'outlet': 'The Wall Street Journal',
            'title': 'New AI Rules Could Reshape Tech Industry Landscape',
            'text': '''The Biden administration's new artificial intelligence regulations are expected to significantly impact the technology industry, potentially creating winners and losers in the rapidly evolving AI market.

The regulations, which will require companies to submit AI systems for government review, could benefit established tech giants with resources to navigate the compliance process while posing challenges for smaller startups.

"Large companies like Google and Microsoft have the legal and compliance teams to handle these regulations," said tech industry analyst Michael Brown. "Smaller AI startups may struggle with the additional costs and delays."

The rules establish different tiers of oversight based on AI system capabilities and use cases. Systems used in critical infrastructure, healthcare, and financial services will face the most stringent requirements.

Industry executives are already planning for the new regulatory environment. "We've been preparing for this for months," said TechInnovate CEO Jennifer Lee. "The key is understanding how to work within the framework while continuing to innovate."

Some investors are concerned about the impact on AI startup funding. "Regulatory uncertainty makes it harder to evaluate AI investments," said venture capitalist Robert Davis. "We need to see how these rules are implemented in practice."

The regulations also establish an AI Safety Board with industry representation, which some see as a positive development. "Having industry voices at the table will help ensure the regulations are practical and effective," said AI Ethics Institute director Dr. Sarah Wilson.''',
            'author': 'Amanda Chen',
            'published_at': datetime.now() - timedelta(hours=5)
        }
    ]
    
    # Insert articles
    article_ids = []
    for article in demo_articles:
        try:
            article_id = db.insert_article(
                url=article['url'],
                outlet=article['outlet'],
                title=article['title'],
                text=article['text'],
                author=article['author'],
                published_at=article['published_at']
            )
            article_ids.append(article_id)
            print(f"Inserted article: {article['title'][:50]}.")
        except Exception as e:
            print(f"Error inserting article: {e}")
    
    return article_ids

def create_demo_bias_scores(article_ids):
    """Create sample bias scores for demo articles"""
    db = StoryGenomeDB()
    
    # Sample bias scores for each outlet
    bias_scores = {
        'CNN': {
            'scores': {'framing': 3, 'omission': 2, 'tone': 3, 'source_selection': 3, 'word_choice': 2},
            'justifications': {
                'framing': 'Presents AI regulation as necessary protection with balanced perspective.',
                'omission': 'Includes both industry and consumer advocate viewpoints.',
                'tone': 'Moderate tone with some emotive language about protection.',
                'source_selection': 'Quotes both supporters and critics of regulations.',
                'word_choice': 'Generally neutral language with some loaded terms like "sweeping".'
            }
        },
        'Fox News': {
            'scores': {'framing': 4, 'omission': 3, 'tone': 4, 'source_selection': 3, 'word_choice': 4},
            'justifications': {
                'framing': 'Frames regulations as government overreach and threat to innovation.',
                'omission': 'Emphasizes negative aspects while downplaying potential benefits.',
                'tone': 'Strongly critical tone with emotive language about government control.',
                'source_selection': 'Heavily favors conservative and industry critics.',
                'word_choice': 'Uses loaded terms like "crackdown", "overreach", "bureaucratic roadblocks".'
            }
        },
        'Reuters': {
            'scores': {'framing': 2, 'omission': 1, 'tone': 1, 'source_selection': 2, 'word_choice': 1},
            'justifications': {
                'framing': 'Neutral presentation of facts without strong editorial slant.',
                'omission': 'Comprehensive coverage of key aspects of the regulations.',
                'tone': 'Objective, factual reporting with minimal emotive language.',
                'source_selection': 'Balanced selection of sources from different perspectives.',
                'word_choice': 'Neutral, precise language appropriate for wire service.'
            }
        },
        'The New York Times': {
            'scores': {'framing': 3, 'omission': 2, 'tone': 2, 'source_selection': 3, 'word_choice': 2},
            'justifications': {
                'framing': 'Presents regulations as thoughtful and comprehensive approach.',
                'omission': 'Good coverage but emphasizes positive aspects of regulations.',
                'tone': 'Generally neutral with slight positive framing.',
                'source_selection': 'Includes diverse sources but leans toward supporters.',
                'word_choice': 'Mostly neutral language with some positive framing terms.'
            }
        },
        'The Wall Street Journal': {
            'scores': {'framing': 3, 'omission': 2, 'tone': 2, 'source_selection': 3, 'word_choice': 2},
            'justifications': {
                'framing': 'Business-focused framing emphasizing industry impact.',
                'omission': 'Good coverage of business implications, less on social aspects.',
                'tone': 'Analytical tone appropriate for business publication.',
                'source_selection': 'Heavy on industry and business sources.',
                'word_choice': 'Business-oriented language with some technical terms.'
            }
        }
    }
    
    # Get articles to match with scores
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT id, outlet FROM articles WHERE id IN ({})".format(
            ','.join('?' * len(article_ids))), article_ids)
        articles = cursor.fetchall()
    
    # Insert bias scores
    for article_id, outlet in articles:
        if outlet in bias_scores:
            scores = bias_scores[outlet]['scores']
            justifications = bias_scores[outlet]['justifications']
            
            db.insert_bias_scores(article_id, scores, justifications)
    
    # Create sample bias phrases
    sample_phrases = [
        {'text': 'sweeping new regulations', 'dimension': 'word_choice'},
        {'text': 'essential for protecting American workers', 'dimension': 'framing'},
        {'text': 'heavy-handed approach', 'dimension': 'tone'},
        {'text': 'government overreach', 'dimension': 'framing'},
        {'text': 'balanced approach to AI governance', 'dimension': 'framing'},
        {'text': 'thoughtful approach to a complex challenge', 'dimension': 'tone'},
        {'text': 'comprehensive framework', 'dimension': 'word_choice'},
        {'text': 'regulatory uncertainty', 'dimension': 'word_choice'}
    ]
    
    # Add phrases to articles
    for article_id in article_ids:
        phrases_to_add = random.sample(sample_phrases, random.randint(2, 4))
        db.insert_bias_phrases(article_id, phrases_to_add)

def create_demo_clusters(article_ids):
    """Create a demo cluster for the AI regulation articles"""
    db = StoryGenomeDB()
    
    # Create a cluster
    with db.get_connection() as conn:
        conn.execute("INSERT INTO clusters (cluster_id, label) VALUES (?, ?)", 
                    (1, "AI Regulation Policy"))
        
        # Add all articles to the cluster
        for article_id in article_ids:
            conn.execute("INSERT INTO cluster_members (cluster_id, article_id) VALUES (?, ?)", 
                        (1, article_id))
    
    pass

def main():
    """Create complete demo dataset"""
    print("Creating demo data for StoryGenome...")
    
    # Create articles
    article_ids = create_demo_articles()
    
    if article_ids:
        # Create bias scores
        create_demo_bias_scores(article_ids)
        
        # Create clusters
        create_demo_clusters(article_ids)
    else:
        print("Failed to create demo articles")

if __name__ == "__main__":
    main()
