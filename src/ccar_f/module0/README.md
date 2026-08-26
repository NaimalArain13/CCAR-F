# Module 0 — Agentic Loop (Foundation)

## Concept

Jab Claude ko **tools** diye jaate hain, to Claude aur hamare code ke darmiyan ek
**agentic loop** chalta hai — ek cycle jo tab tak repeat hota hai jab tak Claude
ka kaam poora na ho jaaye.

Loop ke steps:
1. Hum Claude ko ek message + tools ki list bhejte hain.
2. Claude ya to seedha text jawab deta hai, ya kehta hai "pehle yeh tool call karo".
3. Agar tool call chahiye, **hamara apna code** woh function chalata hai (Claude
   khud function execute nahi karta — woh sirf naam aur input batata hai).
4. Hum function ka result Claude ko wapas bhejte hain.
5. Claude decide karta hai — ya koi aur tool call kare, ya final jawab de de.
6. Yeh tab tak chalta hai jab tak Claude "main done hoon" na keh de.

## Jargon (exam-relevant terms)

| Term | Matlab |
|---|---|
| `stop_reason` | API response ka field jo batata hai Claude ne generation kyun roka. Values: `tool_use`, `end_turn`, `max_tokens` |
| `tool_use` | Response ke `content` array mein content block type — Claude jab tool call karna chahta hai to yeh block bhejta hai (`id`, `name`, `input`) |
| `tool_use_id` | Har `tool_use` block ka unique id — result wapas bhejte waqt yeh id reference hoti hai taake Claude ko pata chale kis call ka result hai |
| `tool_result` | Naye message mein content block type jisme humne apne function ka output daal kar Claude ko wapas bhejna hota hai |
| `end_turn` | `stop_reason` ki value jo batati hai Claude ka turn poora ho gaya — final jawab mil chuka, ab koi tool call nahi |

## Hands-on: Project 1 — Agentic Loop by hand

File: `agentic_loop.py`

Raw Messages API se, bina kisi framework/Agent SDK ke, ek `get_weather` tool
(fake data) ke sath poora loop khud likha gaya — taake underlying mechanics
samajh aayein jo exam directly test karta hai.

Run: `uv run python src/ccar_f/module0/agentic_loop.py`

### Trace (expected flow)
1. User message: "Karachi ka weather kaisa hai abhi?"
2. 1st API call -> `stop_reason: tool_use` (Claude weather nahi janta, tool mangta hai)
3. Hamara `get_weather("Karachi")` function chalta hai (local, fake data)
4. Result `tool_result` block mein `tool_use_id` ke sath wapas bheja jata hai
5. 2nd API call -> `stop_reason: end_turn` (final natural-language jawab)

## Actual Run Output (verified 2026-08-27)

**Iteration 1:**
- `stop_reason -> tool_use`
- `tool_use` block: `name=get_weather`, `input={'city': 'Karachi'}`, `tool_use_id=toolu_01M9nNRktj4JWCXyPBKPjCR1`
- Local function ran (no API call): `get_weather("Karachi")` -> `"34°C, dhoop tez hai (sunny)"`
- `tool_result` sent back referencing the same `tool_use_id`

**Iteration 2:**
- `stop_reason -> end_turn`
- Claude produced its final natural-language answer and the loop broke.

Confirmed: exactly 2 API calls (1 `tool_use` + 1 `end_turn`) for a single-tool question — matches the predicted trace exactly.

Note: Claude replied in Urdu script (not Roman Urdu) — a prompt-engineering/output-language control detail (Domain 4), not an agentic-loop mechanic. Terminal displayed it reversed since it doesn't render RTL text properly.

Status: **Module 0 complete.**
