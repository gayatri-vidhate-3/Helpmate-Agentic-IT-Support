# HelpMate Function Reference

Every Python function now has a docstring with purpose, arguments, return description, and an input/output example or example-use pattern. Examples that require the OpenAI API are illustrative and should be run only after configuring `.env`.

## Module map

- `main.py`: CLI entry point; choose one scenario or run evaluation.
- `agent.py`: end-to-end orchestrator; evidence collection, recovery, draft, critic, actions, and audit output.
- `agents/coordinator_agent.py`: dynamic OpenAI tool selection and execution loop.
- `agents/resolution_worker.py`: creates a structured resolution/RCA draft.
- `agents/critic_agent.py`: validates required sections and source citations.
- `retrieval_worker.py`: embedding index and semantic search across ticket/KB/resolution data.
- `tools.py`: available tool schemas and safe mock action dispatch.
- `openai_http.py`: small standard-library HTTP client for OpenAI API.
- `memory.py`: short-term run memory and persistent case summaries.
- `data_setup.py`: creates synthetic demo datasets when absent.
- `config.py`: paths, model settings, API configuration and limits.
- `evaluate.py`: executes held-out scenarios and writes evaluation metrics.

## Docstring note

The examples are lightweight usage illustrations. API-backed examples require a valid key and may incur API charges. Do not put API keys in source code or commit `.env`.
