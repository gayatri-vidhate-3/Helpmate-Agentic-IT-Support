"""Explicit local tools. Downstream actions are simulated and never call live systems."""
import csv
from config import DATA_DIR
from retrieval_worker import search


def ticket_lookup(ticket_id):
    """Ticket lookup.

Args:
    ticket_id: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    with (DATA_DIR / 'tickets.csv').open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['ticket_id'].lower() == ticket_id.lower():
                return row
    return {'error': f'Ticket {ticket_id} not found in the indexed synthetic ticket set.'}


def asset_lookup(requester_id):
    """Asset lookup.

Args:
    requester_id: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    with (DATA_DIR / 'assets.csv').open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['requester_id'].lower() == requester_id.lower():
                return row
    return {'requester_id': requester_id, 'result': 'No synthetic CMDB record found', 'mock_data': True}


def search_kb(query):
    """Search kb.

Args:
    query: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return search(query, top_k=2, kind='kb')


def search_past_tickets(query):
    """Search past tickets.

Args:
    query: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return search(query, top_k=2, kind='past_ticket')


def search_tickets(query):
    """Search tickets.

Args:
    query: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return search(query, top_k=2, kind='ticket')


def notify_mock(message, target='IT service desk'):
    """Notify mock.

Args:
    message: Input value. See the caller for the expected structure.
    target: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return {'status': 'MOCKED', 'target': target, 'message': message}


def escalate_mock(ticket_id, reason):
    """Escalate mock.

Args:
    ticket_id: Input value. See the caller for the expected structure.
    reason: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return {'status': 'MOCKED', 'escalation_id': 'ESC-' + ticket_id, 'reason': reason}


def approval_mock(ticket_id, reason):
    """Approval mock.

Args:
    ticket_id: Input value. See the caller for the expected structure.
    reason: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return {'status': 'MOCKED', 'approval_required': True, 'ticket_id': ticket_id, 'reason': reason}


def update_ticket_mock(ticket_id, note):
    """Update ticket mock.

Args:
    ticket_id: Input value. See the caller for the expected structure.
    note: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    return {'status': 'MOCKED', 'ticket_id': ticket_id, 'note': 'Prepared draft only; no live ticket changed.'}
FUNCTIONS = {'ticket_lookup': ticket_lookup, 'asset_lookup': asset_lookup, 'search_kb': search_kb, 'search_past_tickets': search_past_tickets, 'search_tickets': search_tickets, 'notify_mock': notify_mock, 'escalate_mock': escalate_mock, 'human_approval_mock': approval_mock, 'prepare_ticket_update_mock': update_ticket_mock}
TOOL_SCHEMAS = [{'type': 'function', 'function': {'name': 'ticket_lookup', 'description': 'Look up an ordinary ticket by ID when more structured details are needed.', 'parameters': {'type': 'object', 'properties': {'ticket_id': {'type': 'string'}}, 'required': ['ticket_id'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'asset_lookup', 'description': 'Look up synthetic CMDB details when device/requester context would help.', 'parameters': {'type': 'object', 'properties': {'requester_id': {'type': 'string'}}, 'required': ['requester_id'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'search_kb', 'description': 'Semantic search of approved IT knowledge-base articles. Reformulate query if evidence is weak.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'search_past_tickets', 'description': 'Semantic search of past resolved tickets and their resolution notes.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'search_tickets', 'description': 'Semantic search of ordinary tickets to identify scope or recurring incidents.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'human_approval_mock', 'description': 'Request human approval before a high-impact, privileged, uncertain, or consequential action.', 'parameters': {'type': 'object', 'properties': {'ticket_id': {'type': 'string'}, 'reason': {'type': 'string'}}, 'required': ['ticket_id', 'reason'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'escalate_mock', 'description': 'Create a simulated escalation/problem record when evidence and impact warrant it.', 'parameters': {'type': 'object', 'properties': {'ticket_id': {'type': 'string'}, 'reason': {'type': 'string'}}, 'required': ['ticket_id', 'reason'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'notify_mock', 'description': 'Record a simulated notification to an appropriate support team.', 'parameters': {'type': 'object', 'properties': {'message': {'type': 'string'}, 'target': {'type': 'string'}}, 'required': ['message', 'target'], 'additionalProperties': False}}}, {'type': 'function', 'function': {'name': 'prepare_ticket_update_mock', 'description': 'Prepare a simulated ticket update after drafting; never changes a live ticket.', 'parameters': {'type': 'object', 'properties': {'ticket_id': {'type': 'string'}, 'note': {'type': 'string'}}, 'required': ['ticket_id', 'note'], 'additionalProperties': False}}}]


def dispatch(name, args):
    """Dispatch.

Args:
    name: Input value. See the caller for the expected structure.
    args: Input value. See the caller for the expected structure.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    if name not in FUNCTIONS:
        return {'error': 'Tool is not allow-listed.'}
    return FUNCTIONS[name](**args)
