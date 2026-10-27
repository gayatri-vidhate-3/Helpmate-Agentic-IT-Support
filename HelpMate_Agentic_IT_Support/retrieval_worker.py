"""Semantic retrieval worker: embeddings + cosine similarity + persistent cache."""
import csv, json, math
from config import DATA_DIR
from openai_http import embed_texts
from data_setup import ensure_data
CACHE = DATA_DIR / 'embeddings_cache.json'


def load_corpus():
    """Load corpus.

Args:
    None.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    ensure_data()
    docs = []
    for item in json.loads((DATA_DIR / 'historical_resolutions.json').read_text(encoding='utf-8')):
        docs.append({'id': item['ticket_id'], 'kind': 'past_ticket', 'text': f"{item['category']}. {item['subject']}. {item['description']}. Resolution: {item['resolution_note']}", 'metadata': item})
    for item in json.loads((DATA_DIR / 'kb_articles.json').read_text(encoding='utf-8')):
        docs.append({'id': item['id'], 'kind': 'kb', 'text': f"{item['title']}. Category: {item['category']}. {item['content']}", 'metadata': item})
    with (DATA_DIR / 'tickets.csv').open(newline='', encoding='utf-8') as f:
        for x in csv.DictReader(f):
            docs.append({'id': x['ticket_id'], 'kind': 'ticket', 'text': f"{x['category']}. {x['subject']}. {x['description']}. System: {x['affected_system']}", 'metadata': x})
    return docs


def _cos(a, b):
    """ cos.

Args:
    a: Input value. See the caller for the expected structure.
    b: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    dot = sum((x * y for x, y in zip(a, b)))
    na = math.sqrt(sum((x * x for x in a)))
    nb = math.sqrt(sum((x * x for x in b)))
    return dot / (na * nb) if na and nb else 0.0


def build_index(force=False):
    """Build index.

Args:
    force: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    docs = load_corpus()
    signature = [d['id'] + ':' + d['text'] for d in docs]
    if CACHE.exists() and (not force):
        try:
            old = json.loads(CACHE.read_text(encoding='utf-8'))
            if old.get('signature') == signature:
                return len(old['documents'])
        except (ValueError, OSError):
            pass
    vec = []
    for start in range(0, len(docs), 64):
        vec.extend(embed_texts([d['text'] for d in docs[start:start + 64]]))
    for d, v in zip(docs, vec):
        d['embedding'] = v
    CACHE.write_text(json.dumps({'signature': signature, 'documents': docs}, ensure_ascii=False), encoding='utf-8')
    return len(docs)


def search(query, top_k=2, kind=None):
    """Search.

Args:
    query: Input value. See the caller for the expected structure.
    top_k: Input value. See the caller for the expected structure.
    kind: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    if not CACHE.exists():
        build_index()
    data = json.loads(CACHE.read_text(encoding='utf-8'))
    q = embed_texts([query])[0]
    found = []
    for d in data['documents']:
        if kind and d['kind'] != kind:
            continue
        score = _cos(q, d['embedding'])
        meta = {k: v for k, v in d.get('metadata', {}).items() if k in ('ticket_id', 'category', 'subject', 'resolution_note', 'id', 'title', 'content', 'affected_system', 'priority', 'status', 'case_id')}
        found.append({'id': d['id'], 'kind': d['kind'], 'score': round(score, 4), 'text': d['text'][:320], 'metadata': meta})
    found.sort(key=lambda x: x['score'], reverse=True)
    return found[:top_k]
