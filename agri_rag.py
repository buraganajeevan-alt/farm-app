"""agri_rag.py — RAG (Retrieval-Augmented Generation) Knowledge Pipeline with Live Web Fallback.
1. Indexes local domain documents in data/knowledge/ using TF-IDF vector embeddings & Cosine Similarity.
2. If the query is related to farming/agriculture but NOT present locally (similarity below threshold),
   it dynamically retrieves live verified agricultural data from the web (DuckDuckGo / Wikipedia).
3. Automatically caches web findings into data/knowledge/web_cache/ so the system self-learns.
"""
import os
import glob
import re
import logging
from typing import List, Dict, Tuple
import numpy as np
import requests

logger = logging.getLogger(__name__)

_PASSAGES: List[Dict[str, str]] = []
_VECTORIZER = None
_DOC_MATRIX = None
_INITIALIZED = False

AGRI_KEYWORDS = {
    "crop", "crops", "soil", "npk", "fertilizer", "fertilizers", "urea", "dap", "potash", "nitrogen",
    "phosphorus", "potassium", "pesticide", "pesticides", "fungicide", "herbicide", "pest", "pests",
    "disease", "diseases", "blight", "blast", "rust", "rot", "wilt", "borer", "armyworm", "whitefly",
    "thrips", "aphid", "mite", "caterpillar", "wheat", "paddy", "rice", "cotton", "chilli", "chili",
    "maize", "corn", "groundnut", "peanut", "sugarcane", "mustard", "millet", "jowar", "bajra", "ragi",
    "soybean", "pulses", "gram", "tur", "moong", "urad", "dragon fruit", "mango", "banana", "citrus",
    "papaya", "guava", "onion", "tomato", "potato", "harvest", "harvesting", "sowing", "plantation",
    "irrigation", "drip", "sprinkler", "monsoon", "rainfall", "weather", "kisan", "farmer", "farmers",
    "farming", "agriculture", "agronomy", "pmkisan", "pm-kisan", "pmfby", "mandi", "msp", "shc",
    "yield", "acre", "hectare", "jeevamrutha", "organic", "compost", "manure", "seed", "seeds",
    "pruning", "grafting", "greenhouse", "polyhouse", "horticulture", "floriculture", "silkworm",
    "dairy", "cattle", "cow", "buffalo", "poultry", "goat", "sheep", "fodder", "hydroponics"
}


def is_agriculture_related(query: str) -> bool:
    """Detects whether a query is related to farming, crops, livestock, fertilizers, or agriculture."""
    q = (query or "").lower().strip()
    if not q:
        return False
    tokens = set(re.findall(r'\b[a-z]{3,}\b', q))
    if tokens & AGRI_KEYWORDS:
        return True
    for kw in AGRI_KEYWORDS:
        if kw in q:
            return True
    return False


def _load_and_chunk_documents() -> List[Dict[str, str]]:
    """Loads markdown documents from data/knowledge/ (including web_cache/) and chunks them by headers."""
    passages = []
    base_dir = os.path.join(os.path.dirname(__file__), "data", "knowledge")
    
    if not os.path.exists(base_dir):
        logger.warning("Knowledge directory not found: %s", base_dir)
        return passages

    # Search knowledge root and web_cache subdirectory
    pattern = os.path.join(base_dir, "**", "*.md")
    files = glob.glob(pattern, recursive=True)

    for filepath in files:
        filename = os.path.basename(filepath)
        is_cached = "web_cache" in filepath
        doc_title = ("Web Cache: " if is_cached else "") + filename.replace(".md", "").replace("_", " ").title()
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Split by section headers (##) or paragraphs
            sections = re.split(r'\n(?=##\s+)', content)
            for sec in sections:
                sec_text = sec.strip()
                if len(sec_text) > 30:
                    header_match = re.search(r'^#{1,3}\s+(.+)', sec_text)
                    section_title = header_match.group(1).strip() if header_match else doc_title
                    passages.append({
                        "source": doc_title,
                        "section": section_title,
                        "text": sec_text,
                        "filepath": filename
                    })
        except Exception as e:
            logger.error("Failed reading knowledge file %s: %s", filepath, e)
            
    return passages


def initialize_rag():
    """Initializes or refreshes the vector space index over all knowledge base passages."""
    global _PASSAGES, _VECTORIZER, _DOC_MATRIX, _INITIALIZED
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        _PASSAGES = _load_and_chunk_documents()
        
        if not _PASSAGES:
            logger.warning("No knowledge passages loaded for RAG.")
            _INITIALIZED = False
            return False

        texts = [p["text"] for p in _PASSAGES]
        _VECTORIZER = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        _DOC_MATRIX = _VECTORIZER.fit_transform(texts)
        _INITIALIZED = True
        logger.info("RAG Indexer initialized with %d passages.", len(_PASSAGES))
        return True
    except Exception as e:
        logger.error("RAG Initialization failed: %s", e)
        _INITIALIZED = False
        return False


def retrieve(query: str, top_k: int = 3, min_score: float = 0.05) -> Tuple[List[Dict[str, str]], str]:
    """Retrieves top_k relevant local passages for a query using cosine similarity."""
    global _PASSAGES, _VECTORIZER, _DOC_MATRIX, _INITIALIZED
    
    if not _INITIALIZED:
        if not initialize_rag() or not _PASSAGES:
            return ([], "")

    q = (query or "").strip()
    if not q:
        return ([], "")

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        query_vec = _VECTORIZER.transform([q])
        scores = cosine_similarity(query_vec, _DOC_MATRIX).flatten()
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        context_parts = []
        
        for idx in top_indices:
            score = float(scores[idx])
            if score >= min_score:
                p = _PASSAGES[idx]
                results.append({
                    "source": p["source"],
                    "section": p["section"],
                    "text": p["text"],
                    "score": round(score, 3)
                })
                context_parts.append(f"Source [{p['source']} - {p['section']}]:\n{p['text']}")
                
        formatted_context = "\n\n".join(context_parts)
        return (results, formatted_context)
    except Exception as e:
        logger.error("RAG retrieval error: %s", e)
        return ([], "")


def search_web_agri(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Live web search fallback for agricultural queries not found in local RAG."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 SmartFarmingBot/1.0'
    }
    web_results = []
    clean_q = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()

    # 1. DuckDuckGo Search (via DuckDuckGo HTML POST)
    try:
        ddg_url = 'https://html.duckduckgo.com/html/'
        r = requests.post(ddg_url, data={'q': f"{clean_q} agriculture farming India"}, headers=headers, timeout=8)
        if r.status_code == 200:
            snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', r.text, re.DOTALL)
            for s in snippets[:max_results]:
                text = re.sub(r'<[^>]+>', '', s).strip()
                if len(text) > 40:
                    web_results.append({
                        "source": "Live Agricultural Web Search (DuckDuckGo)",
                        "section": "Web Finding",
                        "text": text,
                        "score": 0.99
                    })
    except Exception as e:
        logger.debug("DDG web search timeout/error: %s", e)

    # 2. Wikipedia Encyclopedic Search (High reliability fallback)
    if len(web_results) < 2:
        try:
            wiki_url = 'https://en.wikipedia.org/w/api.php'
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': f"{clean_q} agriculture",
                'format': 'json',
                'utf8': 1
            }
            r = requests.get(wiki_url, params=params, headers={'User-Agent': 'SmartFarmingBot/1.0 (https://smartfarming.local)'}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('query', {}).get('search', [])[:max_results]:
                    title = item.get('title', '')
                    snippet = re.sub(r'<[^>]+>', '', item.get('snippet', '')).strip()
                    if snippet and len(snippet) > 30:
                        web_results.append({
                            "source": f"Live Web Knowledge (Wikipedia: {title})",
                            "section": title,
                            "text": f"{title}: {snippet}",
                            "score": 0.95
                        })
        except Exception as e:
            logger.debug("Wiki web search timeout/error: %s", e)

    return web_results


def save_to_web_cache(query: str, results: List[Dict[str, str]]):
    """Caches web search findings to disk in data/knowledge/web_cache/ for instant local retrieval in future."""
    if not results:
        return
    try:
        cache_dir = os.path.join(os.path.dirname(__file__), "data", "knowledge", "web_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', query.lower()).strip('_')[:40]
        filepath = os.path.join(cache_dir, f"{slug}.md")
        
        content = f"# Web Knowledge: {query.title()}\n\n"
        for r in results:
            content += f"## {r['section']}\nSource: {r['source']}\n\n{r['text']}\n\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Re-initialize RAG index so new cached knowledge is immediately searchable
        initialize_rag()
        logger.info("Saved query '%s' to RAG web cache: %s", query, filepath)
    except Exception as e:
        logger.warning("Failed saving to web cache: %s", e)


def has_substantive_match(query: str, passage_text: str) -> bool:
    """Verifies that key substantive subject words from the query actually appear in the matched document."""
    generic_words = {
        "farming", "cultivation", "harvest", "harvesting", "crops", "crop", "agriculture", "india",
        "indian", "control", "treat", "treatment", "price", "method", "best", "give", "tell", "what",
        "which", "when", "where", "guide", "guidelines", "information", "details", "scheme", "advisory"
    }
    q_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()) if w not in generic_words]
    if not q_words:
        return True
    p_lower = passage_text.lower()
    matched_count = sum(1 for w in q_words if w in p_lower)
    return matched_count >= max(1, len(q_words) // 2)


def retrieve_hybrid(query: str, top_k: int = 3, min_local_score: float = 0.12) -> Tuple[List[Dict[str, str]], str, str]:
    """
    Hybrid RAG with Live Web Fallback:
    1. Searches local RAG documents using vector similarity.
    2. Validates that local match is genuine (score >= threshold and key subject words match).
    3. If local match is insufficient AND query is agriculture-related, searches the web!
    4. Auto-caches web findings into data/knowledge/web_cache/ for self-learning.
    
    Returns: (results_list, formatted_context_str, source_type: 'local' | 'web' | 'none')
    """
    local_results, local_context = retrieve(query, top_k=top_k, min_score=min_local_score)
    
    # Check if local RAG has a confident, genuine subject match
    if local_results and local_results[0].get("score", 0) >= min_local_score:
        top_text = local_results[0].get("text", "")
        if has_substantive_match(query, top_text):
            return (local_results, local_context, "local")

    # Local documents don't have this topic — check if related to farming/agriculture
    if is_agriculture_related(query):
        logger.info("Local RAG missing subject for query '%s'. Triggering Live Web Search...", query)
        web_results = search_web_agri(query, max_results=top_k)
        
        if web_results:
            context_parts = [f"Source [{r['source']} - {r['section']}]:\n{r['text']}" for r in web_results]
            web_context = "\n\n".join(context_parts)
            
            # Auto-cache to disk asynchronously
            save_to_web_cache(query, web_results)
            return (web_results, web_context, "web")

    # If non-agricultural or web search returned nothing, return whatever local result existed or empty
    if local_results:
        return (local_results, local_context, "local")
    return ([], "", "none")


# Auto-initialize on import
initialize_rag()
