# Module 1 — Domain 1: Agentic Architecture & Orchestration (27% — highest weight)

## Concept

This domain covers 7 Task Statements (1.1–1.7). Module 0 already covered 1.1
(the raw agentic loop). This module covers the rest.

### 1.1 — Agentic Loop (recap, done in Module 0)
Check `stop_reason`, run the tool on `tool_use`, stop on `end_turn`. Anti-patterns:
don't parse Claude's text output to decide when to stop, and don't rely on an
arbitrary iteration cap as the primary stopping mechanism.

### 1.2 — Coordinator-Subagent Pattern
- **Coordinator** — the "boss" agent that does task decomposition, delegates
  work to subagents, and aggregates their results.
- **Hub-and-spoke architecture** — all communication goes through the
  coordinator; subagents never talk to each other directly. This keeps
  observability and error handling centralized.
- **Isolated context** — a subagent does NOT automatically inherit the
  coordinator's conversation history. It only knows what's explicitly put in
  its own prompt.
- Anti-pattern: decomposing a broad topic too narrowly leads to incomplete
  coverage — the coordinator should dynamically decide how many/which
  subagents are needed.

### 1.3 — Subagent Invocation, Context Passing, Spawning
- **`Task` tool** — the mechanism a coordinator uses to spawn a subagent (a
  Claude Code / Agent SDK feature — requires `"Task"` in `allowedTools`).
- **`AgentDefinition`** — config for a subagent type: system prompt,
  description, tool restrictions.
- Context must be explicitly passed into a subagent's prompt — nothing is
  inherited automatically.
- Best practice: keep content and metadata (source, doc name, page number)
  separate when passing findings between agents, to preserve attribution.
- Parallel subagents are spawned by emitting multiple `Task` calls in a
  single coordinator response, not across separate turns.
- **`fork_session`** — branching off an independent session from a shared
  analysis baseline to explore divergent approaches.

### 1.4 — Multi-Step Workflows: Enforcement & Handoff
- **Programmatic enforcement** (hooks, prerequisite gates) vs **prompt-based
  guidance** — prompts alone have a non-zero failure rate; deterministic
  compliance (e.g. verify identity before a refund) needs code-level
  enforcement, not just instructions.
- **Handoff protocol** — a structured summary (customer ID, root cause,
  recommended action) compiled when escalating to a human who has no access
  to the conversation transcript.
- Covered hands-on in Project 2 (Governed Customer-Support Agent).

### 1.5 — Agent SDK Hooks
- **`PreToolUse`** / **`PostToolUse`** — hooks that intercept a tool call
  before/after it runs, to enforce compliance rules (block a >$500 refund)
  or normalize heterogeneous data formats from different tools.
- Core distinction: hooks give a **deterministic guarantee**; prompts only
  give **probabilistic compliance**.
- Covered hands-on in Project 2.

### 1.6 — Task Decomposition Strategies
- **Prompt chaining** — fixed sequential steps, used when the workflow is
  predictable (e.g. analyze each file, then a cross-file integration pass).
- **Dynamic/adaptive decomposition** — used for open-ended tasks, where the
  plan adapts as new things are discovered (e.g. "add tests to a legacy
  codebase").

### 1.7 — Session State, Resumption, Forking
- **`--resume <session-name>`** — continue a specific prior conversation.
- **`fork_session`** — branch off from a shared baseline.
- When resuming after code changes, explicitly tell the agent what changed —
  don't make it rediscover everything. If prior tool results are stale,
  starting a new session with a structured summary is more reliable than
  resuming.

## Jargon Summary

| Term | Meaning |
|---|---|
| Coordinator | Boss agent that decomposes, delegates, aggregates |
| Hub-and-spoke | All subagent communication routes through the coordinator |
| Isolated context | A subagent doesn't automatically inherit the coordinator's history |
| `Task` tool | Mechanism to spawn a subagent (Claude Code / Agent SDK) |
| `AgentDefinition` | A subagent's config (prompt, tools, description) |
| `fork_session` | Branch an independent session from a shared baseline |
| Handoff protocol | Structured summary compiled for human escalation |
| `PreToolUse` / `PostToolUse` | Hooks that intercept a tool call before/after execution |
| Prompt chaining | Fixed sequential pipeline of steps |
| Dynamic decomposition | Plan that adapts as findings emerge |
| `--resume` | Continue a named prior session |

## Hands-on: Exercise 4 — Multi-Agent Research Pipeline

File: `research_pipeline.py`

Built by hand with the raw Messages API (no Agent SDK `Task` tool, since
that's a Claude Code-specific feature) to manually simulate the
coordinator-subagent pattern and see the mechanics directly. Covers Task
Statements 1.2, 1.3, and 1.6. Statements 1.4, 1.5, 1.7 (hooks, enforcement,
session resumption) are covered hands-on in Project 2 instead.

### Design
A research question is decomposed by a coordinator into 2 subtopics, each
investigated by an independent subagent, then synthesized back by the
coordinator into one final answer.

### Code walkthrough
- `RESEARCH_QUESTION` — the test question given to the coordinator.
- `COORDINATOR_DECOMPOSE_PROMPT` — coordinator's system prompt, forced into a
  strict `SUBTOPIC_A:` / `SUBTOPIC_B:` format so the code can parse it.
- `SUBAGENT_SYSTEM_PROMPT` — explicitly tells the subagent it only knows its
  own assigned topic — this is what enforces isolated context.
- `call_coordinator_decompose()` — 1st API call: sends the full question,
  gets back 2 subtopics.
- `parse_subtopics()` — no API call, just local string parsing of the
  coordinator's response.
- `call_subagent()` — called twice, once per subtopic. Each call builds a
  brand-new `messages` list containing ONLY that subtopic — nothing about
  the original question or the other subagent. This is isolated context
  implemented directly in code.
- `call_coordinator_synthesize()` — combines both findings into one
  structured text block, each labeled with its source subagent (metadata
  separation for attribution), then asks the coordinator for a final answer
  that cites which subagent contributed which point.
- `run_pipeline()` — runs the full sequence and prints every step.

**Total: 4 Haiku API calls** (max_tokens 100/200/200/400) — minimal cost.

Run: `uv run python src/ccar_f/module1/research_pipeline.py`

## Actual Run Output (verified 2026-08-27)

**Coordinator decomposition:**
```
SUBTOPIC_A: Performance and capability differences in understanding customer queries and generating accurate support responses
SUBTOPIC_B: Cost, speed, and resource efficiency tradeoffs for production deployment at scale
```

**Subagent A** (isolated context) produced a finding about model scale/capability
in customer support generally. **Subagent B** (isolated context) produced a
finding about cost/speed/resource tradeoffs at production scale generally.

**Coordinator synthesis** combined both into a Sonnet-vs-Haiku recommendation
for a startup chatbot, citing "Subagent A" and "Subagent B" by name.

Confirmed: 4 API calls total, exactly as designed (1 decompose + 2 subagents + 1 synthesize).

### Unplanned finding: a real isolated-context risk

Neither subagent ever mentioned "Claude Sonnet" or "Claude Haiku" by name —
they wrote generically about "larger models vs smaller models." This is
because only the `subtopic` string was passed into each subagent's prompt,
not the original `RESEARCH_QUESTION` — the product-specific framing never
reached them.

This is Task Statement 1.2's anti-pattern (narrow decomposition losing
coverage) and 1.3's skill (include complete relevant context in the
subagent's prompt) demonstrated directly: isolated context keeps subagents
clean and focused, but if the coordinator under-passes context, the
subagent's output can drift from what's actually needed. The coordinator's
synthesis step had to *assume* which subagent's generic finding mapped to
which product — a real fragility this pattern can introduce if not
designed carefully.

### Second observation: truncation

The final synthesis was cut off mid-sentence because `max_tokens=400` was
too low for the full response — a reminder that `max_tokens` must be sized
to the expected output length or responses truncate silently (no error,
just an incomplete answer with `stop_reason: max_tokens`).

Status: **Exercise 4 complete.**

## Hands-on: Project 2 — Governed Customer-Support Agent

File: `governed_support_agent.py`

Extends the Module 0 agentic loop with a governance layer covering Task
Statements 1.4, 1.5, and 1.7 — manually implemented (raw Messages API), since
real `PreToolUse`/`PostToolUse` hooks and the `Task` tool are Claude Agent
SDK-specific features (see "Deferred" note below).

### Design
Two tools: `get_customer` (identity lookup) and `process_refund`. Three
governance rules enforced in code, not just prompted:
- **Rule A (1.4, prerequisite gate):** `process_refund` is blocked until
  `get_customer` has verified an identity in this conversation.
- **Rule B (1.5, PreToolUse-style block hook):** any refund over
  `REFUND_THRESHOLD` ($500) is blocked before executing, and a structured
  **handoff summary** (1.4) is produced for human escalation instead.
- **Rule C (1.5, PostToolUse-style normalize hook):** `get_customer`'s raw
  Unix timestamp is converted to a readable date before Claude ever sees it.

A lightweight **Task 1.7 demo** saves the conversation's `messages` list to
`session_state.json` and reloads it — the same underlying mechanism
`--resume` uses, with no extra API call needed.

### Actual Run Output (verified 2026-08-27)

**Scenario 1 (Ali, $200 refund):** `get_customer` → `process_refund` →
`end_turn`. All 3 calls succeeded normally; refund allowed since amount was
under threshold and identity was verified first.

**Scenario 2 (Sara, $800 refund):** `get_customer` succeeded, but
`process_refund` was intercepted by the PreToolUse hook (`amount exceeds
auto-approval threshold of $500`) — a handoff summary was printed and the
agent replied that the case was escalated for manual review. **The block
happened in code, before the fake refund function ever ran** — this is the
deterministic-guarantee behavior Task 1.4/1.5 test for.

**Session save/load:** `session_state.json` was written and reloaded (6
messages) with zero additional API calls — confirming session state is just
serialized message history.

Confirmed: 6 API calls total (3 per scenario), matching the design estimate.

### Deferred: practicing with the real Claude Agent SDK

The exam's actual `PreToolUse`/`PostToolUse` hooks and `Task` tool/
`AgentDefinition` are features of the **Claude Agent SDK** (`claude-agent-sdk`
Python package), not the raw Messages API — it wraps the Claude Code CLI as
a subprocess. Naimal already has Claude Code CLI installed locally, so no
new system install is needed, but building a proper hands-on exercise with
the real SDK is its own concept→code→run cycle — **deferred to a later
session** rather than folding it into Module 1's timeline. Note for later:
same `.env`-scoped `ANTHROPIC_API_KEY` works (no global export needed), but
expect ~2-5K tokens/turn overhead from the SDK's injected system
prompt/tool defs vs. our hand-rolled loop.

Status: **Module 1 complete** (Exercise 4 + Project 2 done; real-SDK hooks
practice deferred as a future follow-up).
