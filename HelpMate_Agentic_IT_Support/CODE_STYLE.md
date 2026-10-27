# Code Style and Reading Guide

This project uses plain Python modules and explicit agent classes so the workflow is easy to follow.

## Reading order

1. `main.py` — command-line entry point and demo commands.
2. `agent.py` — connects the agents and manages one ticket run.
3. `agents/coordinator_agent.py` — chooses tools and decides when enough evidence is available.
4. `retrieval_worker.py` — searches tickets, knowledge-base articles, and resolution notes.
5. `agents/resolution_worker.py` — drafts the structured RCA note.
6. `agents/critic_agent.py` — checks the draft for required sections and valid citations.
7. `tools.py` — tool definitions and mock downstream actions.
8. `memory.py` — short-term run notes and saved case summaries.
9. `evaluate.py` — runs the held-out scenarios and writes evaluation results.

## Formatting conventions

- Four spaces per indentation level.
- One statement per line.
- Spaces around operators and after commas.
- Descriptive function and variable names.
- Module and class docstrings describe each component's purpose.
- Comments explain why a step exists, not just what the next line does.

## Important

This formatting pass improves whitespace and statement layout. Always run the included checks and scenario evaluation in your own environment before presenting the project. A clean format does not guarantee that a live API run will succeed.
