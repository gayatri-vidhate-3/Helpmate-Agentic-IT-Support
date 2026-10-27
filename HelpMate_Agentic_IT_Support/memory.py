"""Short-term scratchpad and lightweight long-term case memory."""
import json
from datetime import datetime, timezone
from config import MEMORY_DIR


class AgentMemory:

    def __init__(self, ticket_id):
        """Initialize the object and prepare its dependencies.

Args:
    ticket_id: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
        self.ticket_id = ticket_id
        self.scratchpad = []
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.path = MEMORY_DIR / 'case_memory.json'
        if not self.path.exists():
            self.path.write_text('[]', encoding='utf-8')

    def add(self, kind, detail):
        """Add.

Args:
    kind: Input value. See the caller for the expected structure.
    detail: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
        self.scratchpad.append({'time': datetime.now(timezone.utc).isoformat(), 'kind': kind, 'detail': detail})

    def recall(self, limit=3):
        """Recall.

Args:
    limit: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
        try:
            records = json.loads(self.path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            records = []
        return records[-limit:]

    def remember(self, decision, source_ids, confidence):
        """Remember.

Args:
    decision: Input value. See the caller for the expected structure.
    source_ids: Input value. See the caller for the expected structure.
    confidence: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
        records = self.recall(limit=100000)
        records.append({'time': datetime.now(timezone.utc).isoformat(), 'ticket_id': self.ticket_id, 'decision': decision, 'source_ids': source_ids[:10], 'confidence': confidence})
        self.path.write_text(json.dumps(records[-100:], indent=2), encoding='utf-8')
