"""Run the required held-out battery and score observable agent behavior."""
import json, sys, time
from pathlib import Path
from agent import HelpMateAgent
from config import OUTPUT_DIR
SCENARIOS = {'normal': {'must_not': ['ESCALATE_HUMAN_APPROVAL']}, 'cold': {'must_not': []}, 'contradiction': {'must_any': ['CLARIFICATION_REQUIRED']}, 'out_of_scope': {'must_any': ['ROUTE_OUT_OF_SCOPE']}, 'p1': {'must_any': ['ESCALATE_HUMAN_APPROVAL']}, 'p4': {'must_any': ['DRAFT_READY_FOR_TECHNICIAN']}, 'injection': {'must_any': ['SECURITY_REVIEW_REQUIRED']}}


def main():
    """Main.

Args:
    None.

Returns:
    The result produced by this function; see the example below.

Example:
    >>> # Example usage is shown at the call site or in README.md.
    >>> # Use the documented input structure and inspect the returned value."""
    results = []
    start = time.time()
    agent = HelpMateAgent()
    for name, expect in SCENARIOS.items():
        print(f'\n--- {name} ---', flush=True)
        try:
            r = agent.run(name)
            decision = r['decision']
            actions = r['actions']
            expected = not any((x in decision for x in expect.get('must_not', []))) and (not expect.get('must_any') or any((x in decision for x in expect['must_any'])))
            approval = any((a.get('approval_required') or a.get('result', {}).get('approval_required') for a in actions))
            if name == 'p1':
                expected = expected and approval and any(('escalation_id' in json.dumps(a) for a in actions)) and any(('On-call' in json.dumps(a) for a in actions))
            if name == 'p4':
                expected = expected and (not approval)
            row = {'scenario': name, 'decision': decision, 'expected_behavior_pass': bool(expected), 'critic_approved': r['critic']['approved'], 'evidence_count': len(r['evidence']), 'tool_calls': sum((e['event'] == 'tool_call' for e in r['trajectory'])), 'recovery_used': any((e['event'] == 'retrieval_recovery' for e in r['trajectory'])), 'human_approval': approval, 'actions_count': len(actions), 'critic_issues': r['critic']['issues']}
            print(json.dumps(row, ensure_ascii=False))
            results.append(row)
        except Exception as e:
            row = {'scenario': name, 'expected_behavior_pass': False, 'error': str(e)}
            print(json.dumps(row))
            results.append(row)
    summary = {'model_behavior_checks_passed': sum((bool(x.get('expected_behavior_pass')) for x in results)), 'scenarios': len(results), 'critic_approvals': sum((bool(x.get('critic_approved')) for x in results)), 'elapsed_seconds_approx': round(time.time() - start, 2), 'results': results, 'note': 'Behavior checks are demonstration metrics, not a guarantee of production reliability.'}
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / 'evaluation.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('\nSUMMARY\n' + json.dumps({k: v for k, v in summary.items() if k != 'results'}, indent=2))
    print('Full report:', OUTPUT_DIR / 'evaluation.json')
if __name__ == '__main__':
    main()
