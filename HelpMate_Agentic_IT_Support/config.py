"""Small, dependency-light configuration."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'outputs'
MEMORY_DIR = ROOT / 'memory_store'
ENV_PATH = ROOT / '.env'


def _load_env():
    """ load env.

Args:
    None.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    if ENV_PATH.exists():
        for raw in ENV_PATH.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line and (not line.startswith('#')) and ('=' in line):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"\''))
_load_env()
API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini').strip()
EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small').strip()
MAX_TOOL_ROUNDS = max(1, min(4, int(os.getenv('MAX_TOOL_ROUNDS', '3'))))
