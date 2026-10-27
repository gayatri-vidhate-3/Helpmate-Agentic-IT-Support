# HelpMate — Agentic AI Engineer Assessment

A small, end-to-end IT support agent with dynamic OpenAI function calling, semantic RAG, coordinator–worker–critic roles, memory, mock downstream actions and audit logging. It uses Python's standard library for API requests to avoid heavy dependencies and Windows compiled-extension issues.

## 1. Setup in VS Code (Windows)
1. Unzip the project and open the extracted folder in VS Code.
2. Install Python 3.11 or 3.12 if needed.
3. Open Terminal in VS Code and run `python -m venv .venv`.
4. Activate it in PowerShell: `.\.venv\Scripts\Activate.ps1`. If PowerShell blocks activation, use `\.venv\Scripts\python.exe` directly.
5. Copy `.env.example` to `.env`; put your OpenAI API key in `.env` locally. Do not paste the key into chat or commit `.env`.
6. No pip install is required: this project uses only the Python standard library.
7. Test the key: `python main.py --check-api`.
8. Build the semantic index once: `python main.py --build-index`. This makes embedding API calls and stores a local cache. Reuse it for later runs; `--force-index` rebuilds it and incurs additional API usage.
9. Run one demo: `python main.py --scenario normal`.
10. Run all scenarios: `python evaluate.py`.

If `python` points to the wrong interpreter, use `.\.venv\Scripts\python.exe main.py --scenario normal`.

## 2. Scenarios
`normal`, `cold`, `contradiction`, `out_of_scope`, `p1`, `p4`, `injection`.

## 3. Outputs
- `outputs/latest_run.json`: last ticket, evidence, claims, critic result, mock actions, timestamped trajectory and scratchpad.
- `outputs/run_history.jsonl`: append-only run history.
- `outputs/evaluation.json`: scenario behavior checks.
- `data/embeddings_cache.json`: local semantic index cache (created on first index build).
- `memory_store/case_memory.json`: capped long-term run summaries.

## 4. Speed and API cost
- `gpt-4o-mini` and `text-embedding-3-small` are defaults.
- Index embeddings are cached. Build the index once, not before every demo.
- Top 2 retrieval matches per tool; maximum 3 coordinator rounds; one draft call and at most one revision call.
- Critic is local Python and adds no LLM call.
- Actual runtime depends on network/model latency and whether the index already exists. No runtime or accuracy can be guaranteed in advance.

## 5. What is and is not live
All notifications, ticket updates, escalations and approval requests are MOCKED. No company systems are contacted. Synthetic data is for demonstration only.

## 6. Suggested demo order
1. `normal` — show semantic matches and cited RCA.
2. `cold` — show retrieval recovery/reformulation.
3. `contradiction` — show clarification rather than fabricated root cause.
4. `out_of_scope` — show routing away from IT diagnosis.
5. `p1` — show approval, escalation and notification if agent reasoning identifies broad impact.
6. `p4` — show lighter handling of a how-to request.
7. `injection` — show that ticket-embedded instructions are treated as untrusted.

## 7. Important
The LLM is probabilistic. Read the generated note and evaluation report before presenting. The critic is intentionally simple and is not a substitute for expert validation or production security review.
