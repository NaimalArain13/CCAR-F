import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"

# The single question the whole pipeline is trying to answer.
# NOTE: only this, RESEARCH_QUESTION itself, ever mentions "Sonnet"/"Haiku" by
# name - the subtopics below are deliberately generic (see call_subagent).
RESEARCH_QUESTION = "What are the key differences between Claude Sonnet and Claude Haiku for a startup building a customer support chatbot?"

# Coordinator's system prompt: forces a strict, easily-parseable output format
# (SUBTOPIC_A / SUBTOPIC_B) instead of free-form prose.
COORDINATOR_DECOMPOSE_PROMPT = """You are a research coordinator. Break the user's research question
into exactly 2 focused, non-overlapping subtopics that two independent researchers could investigate
separately. Respond in EXACTLY this format, nothing else:

SUBTOPIC_A: <short phrase>
SUBTOPIC_B: <short phrase>"""

# Subagent's system prompt: explicitly tells it to know NOTHING beyond its own
# topic - this is what enforces "isolated context" at the prompt level.
SUBAGENT_SYSTEM_PROMPT = """You are a focused research subagent. You only know the single topic you
are given below - you have no knowledge of any broader question or other subagents. Write a concise
3-4 sentence finding based on your own knowledge of this topic."""

COORDINATOR_SYNTHESIS_PROMPT = """You are a research coordinator. You were given findings from two
independent subagents, each labeled with their source. Synthesize them into a single coherent answer
to the original research question. Explicitly mention which subagent contributed which point."""


def call_coordinator_decompose(question: str) -> str:
    # API call #1: coordinator turns the full question into 2 subtopics.
    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        system=COORDINATOR_DECOMPOSE_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def parse_subtopics(decomposition_text: str) -> tuple[str, str]:
    # No API call - just local string parsing of the coordinator's fixed-format reply.
    subtopic_a = ""
    subtopic_b = ""
    for line in decomposition_text.splitlines():
        if line.startswith("SUBTOPIC_A:"):
            subtopic_a = line.replace("SUBTOPIC_A:", "").strip()
        elif line.startswith("SUBTOPIC_B:"):
            subtopic_b = line.replace("SUBTOPIC_B:", "").strip()
    return subtopic_a, subtopic_b


def call_subagent(subtopic: str) -> str:
    # Fresh, isolated messages list -> this subagent has ZERO knowledge of the
    # coordinator's original question or the other subagent's existence.
    # (This is also why the real output ended up generic - see module1 README.)
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SUBAGENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Your assigned topic: {subtopic}"}],
    )
    return response.content[0].text


def call_coordinator_synthesize(question: str, finding_a: str, subtopic_a: str, finding_b: str, subtopic_b: str) -> str:
    # Structured context: content (the finding) kept separate from its
    # metadata (which subagent/subtopic it came from) - preserves attribution.
    structured_context = f"""Original research question: {question}

Finding from Subagent A (topic: {subtopic_a}):
{finding_a}

Finding from Subagent B (topic: {subtopic_b}):
{finding_b}"""

    # API call #4: coordinator aggregates both findings into one final answer.
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=COORDINATOR_SYNTHESIS_PROMPT,
        messages=[{"role": "user", "content": structured_context}],
    )
    return response.content[0].text


def run_pipeline():
    print(f"[Original Question] -> {RESEARCH_QUESTION}\n")

    decomposition = call_coordinator_decompose(RESEARCH_QUESTION)
    print(f"[Coordinator: Task Decomposition] ->\n{decomposition}\n")

    subtopic_a, subtopic_b = parse_subtopics(decomposition)
    print(f"[Parsed] subtopic_a={subtopic_a!r}, subtopic_b={subtopic_b!r}\n")

    # API calls #2 and #3 - each subagent runs independently (hub-and-spoke:
    # they never call or know about each other, only the coordinator does).
    finding_a = call_subagent(subtopic_a)
    print(f"[Subagent A: Isolated Context] topic={subtopic_a!r} ->\n{finding_a}\n")

    finding_b = call_subagent(subtopic_b)
    print(f"[Subagent B: Isolated Context] topic={subtopic_b!r} ->\n{finding_b}\n")

    final_answer = call_coordinator_synthesize(RESEARCH_QUESTION, finding_a, subtopic_a, finding_b, subtopic_b)
    print(f"[Coordinator: Result Aggregation / Final Synthesis] ->\n{final_answer}\n")


if __name__ == "__main__":
    run_pipeline()
