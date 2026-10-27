# HelpMate Architecture and Assessment Mapping

## Agents
- **CoordinatorAgent** (`agents/coordinator_agent.py`): ReAct-style plan-and-act loop. The model chooses tools and order dynamically using OpenAI function calling. Maximum rounds are configurable; the model may stop early.
- **Retrieval Worker** (`retrieval_worker.py`): builds an embedding index for ordinary tickets, past resolution notes and KB articles; held-out scenarios are excluded. Uses cosine similarity and a local JSON cache.
- **ResolutionWorker** (`agents/resolution_worker.py`): synthesizes the required seven-section RCA note as structured JSON with per-claim source IDs.
- **CriticAgent** (`agents/critic_agent.py`): validates required sections, evidence IDs, claim source IDs, inline citations, and unsafe credential actions. A failed review triggers one bounded revision call and a second review.
- **AgentMemory** (`memory.py`): per-ticket scratchpad plus capped long-term summaries of previous decisions and source IDs.
- **Mock tools** (`tools.py`): ticket lookup, CMDB lookup, KB search, past-ticket search, similar-ticket search, mock notification, mock escalation/problem record, human approval and draft ticket update.

## Agent decision loop
1. Coordinator receives ticket and safe summaries from long-term memory.
2. It chooses tools, calls them and observes results. Weak or empty retrieval triggers one query reformulation/broadening recovery.
3. Resolution Worker drafts the note from ticket plus retrieved evidence only.
4. Critic validates the note. One revision is requested if checks fail.
5. A small deterministic safety layer prevents live side effects and requests approval for uncertain/risky decisions; it does not classify P1 by ticket ID or keyword rule. The agent's decision and impact assessment drive the branch.
6. Every tool call, observation, draft, review, recovery and action is timestamped in `outputs/latest_run.json` and append-only `outputs/run_history.jsonl`.

## Data and retrieval
- 150 synthetic ordinary tickets; 20 past resolution notes; six KB articles; synthetic assets; seven held-out scenarios.
- The held-out scenario file is not indexed. The ordinary ticket corpus, past resolutions and KB articles share ticket/case IDs where applicable.
- Embeddings: `text-embedding-3-small`; generation: `gpt-4o-mini` by default. Both are configurable.
- The embedding cache is built once and reused. Search returns top two results per chosen tool to control latency and prompt size.

## Guardrails and limitations
- Ticket text and retrieved documents are treated as untrusted content, not system instructions.
- Privileged credential changes are not implemented. Every downstream action is simulated; no real ticket, message or escalation system is connected.
- The critic is a lightweight rule-based reviewer, so it is fast and repeatable but cannot guarantee semantic truth. The LLM revision step is bounded to one attempt.
- The audit log stores concise public plans and tool trajectory, not hidden model chain-of-thought.
- Long-term memory stores short run summaries only; do not put secrets or personal data into this synthetic demo.
- For production: authenticate users, apply RBAC, protect secrets, add PII redaction, use a managed vector store/DB, persist trace IDs, add human review UI, monitoring, rate limits, and tests against a versioned evaluation set.

## Requirements covered
- Coordinator/worker/critic roles and real function-calling interface: yes.
- Dynamic tool selection and stop/recovery logic: yes.
- Semantic embedding retrieval and held-out split: yes.
- Seven required note sections and source citations: yes; critic checks IDs and citations.
- Mock notification/escalation/update and human approval: yes.
- Short- and long-term memory: yes.
- Scenarios: normal, cold retrieval, contradictory data, out of scope, P1, P4, injection.
- Evaluation dimensions: observable proxies for tool calls, recovery, escalation, evidence, critic and scenario outcome. Scores should be interpreted as demo checks, not guarantees.
