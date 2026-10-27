"""Standard-library OpenAI HTTP client; avoids SDK/Pydantic compiled dependencies."""
import json, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from config import API_KEY, MODEL, EMBEDDING_MODEL


class OpenAIAPIError(RuntimeError):
    pass


def _post(path, payload, timeout=60, retries=1):
    """ post.

Args:
    path: Input value. See the caller for the expected structure.
    payload: Input value. See the caller for the expected structure.
    timeout: Input value. See the caller for the expected structure.
    retries: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    if not API_KEY:
        raise OpenAIAPIError('OPENAI_API_KEY missing. Copy .env.example to .env and add your key locally.')
    req = Request('https://api.openai.com/v1' + path, data=json.dumps(payload).encode(), headers={'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'HelpMate-Assessment/2.0'}, method='POST')
    for attempt in range(retries + 1):
        try:
            with urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            detail = e.read().decode(errors='replace')
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(1 + attempt)
                continue
            raise OpenAIAPIError(f'OpenAI API HTTP {e.code}: {detail[:900]}') from e
        except (URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(1 + attempt)
                continue
            raise OpenAIAPIError(f'Network error calling OpenAI: {e}') from e


def chat(messages, tools=None, max_tokens=450, temperature=0):
    """Chat.

Args:
    messages: Input value. See the caller for the expected structure.
    tools: Input value. See the caller for the expected structure.
    max_tokens: Input value. See the caller for the expected structure.
    temperature: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    body = {'model': MODEL, 'messages': messages, 'temperature': temperature, 'max_tokens': max_tokens}
    if tools:
        body.update(tools=tools, tool_choice='auto')
    return _post('/chat/completions', body)['choices'][0]['message']


def embed_texts(texts):
    """Embed texts.

Args:
    texts: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    if not texts:
        return []
    out = _post('/embeddings', {'model': EMBEDDING_MODEL, 'input': texts, 'encoding_format': 'float'}, timeout=90)
    return [x['embedding'] for x in sorted(out['data'], key=lambda x: x['index'])]
