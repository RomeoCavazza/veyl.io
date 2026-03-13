from typing import List, Dict, Any
import spacy
from collections import Counter
from datetime import datetime
from src.utils.logger_v2 import logger  # Use the singleton instance

try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    logger.warning("French language model not found. Downloading...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_sm"])
    nlp = spacy.load("fr_core_news_sm")

def extract_keywords(text: str, n: int = 10) -> List[str]:
    """Extract the most relevant keywords from text."""
    doc = nlp(text)
    words = [token.text.lower() for token in doc 
             if not token.is_stop and not token.is_punct 
             and token.pos_ in ['NOUN', 'PROPN']]
    return [word for word, _ in Counter(words).most_common(n)]

def detect_trends(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect trends in a collection of articles."""
    all_keywords = []
    for article in articles:
        content = article.get("content", "")
        if content:
            keywords = extract_keywords(content)
            all_keywords.extend(keywords)
    
    trends = Counter(all_keywords)
    return {
        "top_keywords": dict(trends.most_common(10)),
        "analysis_date": datetime.now().isoformat(),
        "total_articles": len(articles)
    }

def summarize_items(items: List[Dict[str, Any]], max_length: int = 200) -> List[Dict[str, Any]]:
    """Generate summaries for a list of items."""
    summaries = []
    for item in items:
        doc = nlp(item.get("content", ""))
        summary = " ".join([sent.text for sent in doc.sents][:3])
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        summaries.append({
            "title": item.get("title", ""),
            "summary": summary,
            "source": item.get("source", ""),
            "url": item.get("url", "")
        })
    
    return summaries
