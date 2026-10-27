# HelpMate — Agentic IT Support Resolution Assistant

HelpMate is a Python proof of concept for an agentic IT support assistant. It analyzes synthetic support tickets, retrieves related historical cases and knowledge-base guidance, drafts a structured resolution/root-cause analysis (RCA) note, checks the draft for evidence and safety issues, and selects an appropriate next action.

The project demonstrates an agent workflow built around dynamic tool selection, retrieval-augmented generation (RAG), bounded retrieval recovery, a critic/reviewer, short-term and long-term memory, and timestamped audit records.

## Key capabilities

- **Coordinator–worker–critic architecture:** A coordinator selects tools dynamically, a resolution worker drafts the RCA, and a critic checks structure, citations, and unsafe content.
- **Semantic retrieval:** Uses embeddings and cosine similarity to search synthetic tickets, historical resolution notes, and knowledge-base articles.
- **Evidence-aware RCA notes:** Generates a seven-section report with source IDs and cautious language for uncertain findings.
- **Tool calling:** Includes ticket lookup, asset/CMDB lookup, searches over KB articles and past tickets, and mock notification, escalation, approval, and ticket-update actions.
- **Scenario handling:** Includes normal resolution, cold retrieval, contradictory ticket details, out-of-scope requests, high-priority incidents, low-priority how-to requests, and prompt-injection attempts.
- **Memory and audit trail:** Records per-run scratchpad entries, prior-case summaries, tool calls, observations, decisions, and actions.
- **Evaluation script:** Runs the scenario battery and records observable behavior checks in JSON.

## Architecture

```text
Ticket / Scenario
       |
       v
Coordinator Agent
(dynamic tool selection and bounded tool loop)
       |
       +----> Ticket / Asset Lookup
       +----> Semantic Search: KB / Past Cases / Tickets
       +----> Retrieval Recovery (when appropriate)
       |
       v
Resolution Worker
(structured RCA draft + evidence references)
       |
       v
Critic Agent
(required sections, source IDs, inline citations, safety checks)
       |
       +----> Bounded revision when checks fail
       |
       v
Decision and Mock Actions
(draft for technician / clarification / route / escalation)
       |
       v
Timestamped JSON Run Record and Evaluation
```

## Project structure

```text
HelpMate_OpenAI_Project_GRV/
├── agents/
│   ├── coordinator_agent.py
│   ├── resolution_worker.py
│   └── critic_agent.py
├── data/
│   ├── tickets.csv
│   ├── historical_resolutions.json
│   ├── kb_articles.json
│   ├── assets.csv
│   ├── heldout_scenarios.json
│   └── embeddings_cache.json
├── memory_store/
├── outputs/
├── agent.py
├── config.py
├── data_setup.py
├── evaluate.py
├── main.py
├── memory.py
├── openai_http.py
├── retrieval_worker.py
├── tools.py
├── ARCHITECTURE.md
├── FUNCTION_REFERENCE.md
└── requirements.txt
```

## Technology

- Python 3.11 or 3.12 recommended
- OpenAI Chat Completions API with function calling
- `gpt-4o-mini` as the default generation model
- `text-embedding-3-small` as the default embedding model
- Python standard library for HTTP requests, data handling, JSON/CSV files, and cosine-similarity calculations

The model names can be changed through environment variables. The project does not require third-party Python packages in its current implementation.

## Setup

### 1. Clone or download the repository

Open the project root folder in a terminal or in VS Code.

### 2. Create a virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the project using the virtual environment's Python executable directly.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Configure the API key

Create a file named `.env` in the project root and add your API key locally:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MAX_TOOL_ROUNDS=3
```

Do not commit `.env` or publish your API key. The application reads these values from `.env` when it exists, and environment variables can also be used.

### 4. Check the API connection

```bash
python main.py --check-api
```

### 5. Build the semantic retrieval index

```bash
python main.py --build-index
```

This step calls the embeddings API and stores a local cache in `data/embeddings_cache.json`. Reuse the cache for subsequent runs. To rebuild it after changing the corpus:

```bash
python main.py --force-index
```

API usage may incur charges according to your provider's pricing and account limits.

## Run the scenarios

Run a single scenario:

```bash
python main.py --scenario normal
```

Available scenarios:

| Scenario | Purpose | Expected high-level behavior |
|---|---|---|
| `normal` | Routine VPN connectivity issue | Prepare a technician-ready draft |
| `cold` | Novel remote-access issue with limited evidence | Acknowledge uncertainty and recommend safe next steps |
| `contradiction` | Category conflicts with the issue description | Request clarification |
| `out_of_scope` | Facilities request rather than an IT incident | Route outside the IT incident workflow |
| `p1` | Widespread, high-impact outage | Escalate and require human approval |
| `p4` | Low-priority Outlook how-to request | Use a lighter support path |
| `injection` | Ticket contains suspicious privileged-action instructions | Treat ticket text as untrusted and require security review |

Run the full scenario evaluation:

```bash
python evaluate.py
```

Model responses can vary between runs. Review the generated report and audit trail rather than assuming a scenario has passed solely because the command completed.

## Outputs

- `outputs/latest_run.json` — detailed record for the most recent run, including the ticket, retrieved evidence, generated RCA, critic result, actions, and timestamped trajectory.
- `outputs/run_history.jsonl` — append-only history of runs.
- `outputs/evaluation.json` — scenario-level behavior checks, tool-call counts, evidence counts, critic status, and action summaries.
- `data/embeddings_cache.json` — cached document embeddings and index metadata.
- `memory_store/case_memory.json` — capped summaries of prior run decisions and source IDs.

## RCA note format

Generated reports use these sections:

1. Summary
2. Affected Scope & Environment
3. Diagnosis & Root Cause
4. Resolution / Recommended Fix
5. Verification
6. Preventive Action / KB Update
7. References

The intended behavior is to distinguish reported symptoms, hypotheses, and proposed actions from confirmed findings, and to cite retrieved evidence where applicable.

## Evaluation scope

The included scenario battery checks high-level routing and behavior for seven representative cases. It also records supporting indicators such as tool calls, retrieval recovery events, evidence counts, human-approval signals, and critic results.

These are prototype-level checks, not a comprehensive benchmark or a guarantee of correctness, security, or production readiness. A critic approval means the implemented validation checks passed; it does not independently prove that a diagnosis is true or that an issue has been resolved.

## Safety and current limitations

- **All downstream actions are simulated.** Notifications, ticket updates, escalations, and approval requests do not contact live systems.
- **Data is synthetic.** Tickets, KB articles, historical cases, and asset records are demonstration data, not operational company records.
- **Human review remains important.** The application prepares recommendations; it does not verify real-world remediation.
- **The critic is lightweight.** Rule-based checks can miss unsupported claims or flag acceptable text. It is not a substitute for expert review or a full security evaluation.
- **External integrations are not included.** A production version would need identity and access controls, secure secret management, data privacy controls, a persistent database/vector store, monitoring, tracing, and integration tests.

## Security and Git hygiene

Before publishing, ensure that `.env`, virtual environments, Python cache directories, and any private credentials are excluded from version control. Generated embedding caches and run outputs can be regenerated and may be better kept out of the repository if you want a smaller, cleaner public codebase.

A suitable `.gitignore` should include at least:

```gitignore
.env
.venv/
venv/
__pycache__/
*.py[cod]
```

## Future improvements

- Strengthen critic validation with more robust claim-to-source checks and regression tests.
- Expand the synthetic knowledge corpus and improve relationships between ticket IDs and escalated case/RCA records.
- Add more varied retrieval-failure tests and measure whether recovery actually improves evidence relevance.
- Add unit and integration tests for tool selection, action policy, citation validity, and failure handling.
- Add a configurable persistent vector database and authenticated integrations for a production deployment.

## License

Add a license file if you intend to permit reuse or redistribution. Do not imply a license has been granted until one is selected and included.
