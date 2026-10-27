"""Command line entry point."""
import argparse
from config import API_KEY, OUTPUT_DIR, MODEL
from data_setup import ensure_data
from openai_http import chat
from retrieval_worker import build_index
from agent import HelpMateAgent
SCENARIOS = ['normal', 'cold', 'contradiction', 'out_of_scope', 'p1', 'p4', 'injection']


def main():
    """Main.

Args:
    None.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    p = argparse.ArgumentParser(description='HelpMate agentic IT support proof of concept')
    p.add_argument('--scenario', choices=SCENARIOS, default='normal')
    p.add_argument('--check-api', action='store_true')
    p.add_argument('--build-index', action='store_true')
    p.add_argument('--force-index', action='store_true')
    a = p.parse_args()
    ensure_data()
    if a.check_api:
        print(chat([{'role': 'user', 'content': 'Reply exactly: HelpMate API connection successful.'}], max_tokens=25).get('content'))
        return
    if a.build_index or a.force_index:
        print(f'Semantic index ready: {build_index(force=a.force_index)} documents.')
        return
    if not API_KEY:
        raise SystemExit('OPENAI_API_KEY missing. Copy .env.example to .env and add your key locally.')
    result = HelpMateAgent().run(a.scenario)
    print('\n' + '=' * 72 + '\nHELPMATE RESOLUTION / RCA NOTE\n' + '=' * 72)
    print(result['note'])
    print('\nDecision:', result['decision'], '| Confidence:', result['confidence'])
    print('Critic approved:', result['critic']['approved'], '| Evidence sources:', len(result['evidence']))
    print('Mock actions:', len(result['actions']))
    print('Audit:', OUTPUT_DIR / 'latest_run.json')
if __name__ == '__main__':
    main()
