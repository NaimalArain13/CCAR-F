# CCAR-F

Hands-on prep for the **Claude Certified Architect – Foundations (CCAR-F)** exam —
learning the material the way a Senior Forward Deployed Engineer would: every
concept built and run with the real Claude API, not just read about.

## Exam being targeted

- 60 items + 4 scenarios (from a bank of 6), 120 minutes, passing score 720/1000
- 5 domains: Agentic Architecture & Orchestration (27%), Tool Design & MCP
  Integration (18%), Claude Code Configuration & Workflows (20%), Prompt
  Engineering & Structured Output (20%), Context Management & Reliability (15%)

## Structure

```
src/ccar_f/
  module0/   Agentic loop by hand (stop_reason, tool_use, tool_result, end_turn)
  module1/   Domain 1 — Agentic Architecture & Orchestration
  module2/   Domain 2 — Tool Design & MCP Integration
  module3/   Domain 3 — Claude Code Configuration & Workflows
  module4/   Domain 4 — Prompt Engineering & Structured Output
  module5/   Domain 5 — Context Management & Reliability
  module6/   Scenario practice + full mock exams
```

Each `moduleN/` folder has its own `README.md` with the concept notes,
jargon, and the actual run output for that module's exercise(s) — that's
the permanent record of what was covered, independent of any chat history.

## Setup

Python deps are managed with `uv`.

```bash
uv sync
```

Create a `.env` file (gitignored) with your own key:

```
ANTHROPIC_API_KEY=your-key-here
```

This key is scoped to this project only — it is not registered with Claude
Code or any other Anthropic product, only used by the scripts in `src/`.

## Running an exercise

```bash
uv run python src/ccar_f/moduleN/<script>.py
```

## Status

- **Module 0 — complete.** Raw agentic loop built by hand (no framework),
  verified against real API output. See `src/ccar_f/module0/README.md`.
- Module 1 onward — in progress.
