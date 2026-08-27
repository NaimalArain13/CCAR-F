import json
import os
from datetime import datetime, timezone

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"

# Business rule: refunds above this amount cannot be auto-approved (Task 1.5:
# PreToolUse-style block hook) - this is enforced in code, not just in the prompt.
REFUND_THRESHOLD = 500

SESSION_FILE = "session_state.json"  # where we "save" a conversation to simulate --resume

SYSTEM_PROMPT = """You are a customer support agent. Always verify the customer's identity
using get_customer before processing any refund with process_refund. Keep responses brief."""

# --- Fake tool backends (no real DB/payment system - just enough to demo the loop) ---

FAKE_CUSTOMERS = {
    "ali@example.com": {"customer_id": "CUST-1001", "name": "Ali Raza", "last_purchase_unix": 1719500000},
    "sara@example.com": {"customer_id": "CUST-2002", "name": "Sara Khan", "last_purchase_unix": 1722000000},
}


def get_customer(email: str) -> dict:
    return FAKE_CUSTOMERS.get(email, {"error": "customer not found"})


def process_refund(customer_id: str, amount: float) -> dict:
    return {"status": "success", "customer_id": customer_id, "refunded_amount": amount}


tools = [
    {
        "name": "get_customer",
        "description": "Look up a customer's verified record by email.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
    },
    {
        "name": "process_refund",
        "description": "Process a refund for a verified customer_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["customer_id", "amount"],
        },
    },
]


# --- Hooks (manually implemented here - a raw stand-in for what the Agent SDK's
# PreToolUse/PostToolUse hooks do automatically) ---


def post_tool_use_normalize(tool_name: str, raw_result: dict) -> dict:
    # PostToolUse: transform a tool's raw output before Claude ever sees it.
    # Here get_customer returns a Unix timestamp - we convert it to a readable
    # date, simulating normalizing heterogeneous formats from different tools.
    if tool_name == "get_customer" and "last_purchase_unix" in raw_result:
        normalized = dict(raw_result)
        ts = normalized.pop("last_purchase_unix")
        normalized["last_purchase_date"] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        return normalized
    return raw_result


def pre_tool_use_gate(tool_name: str, tool_input: dict, verified_customer_id: str | None) -> tuple[bool, str | None]:
    # PreToolUse: inspect a tool call BEFORE it runs, and block it if it
    # violates a business rule - regardless of what Claude "intended".
    if tool_name != "process_refund":
        return True, None

    # Rule A - prerequisite gate (Task 1.4): identity must be verified first.
    if verified_customer_id is None:
        return False, "BLOCKED: get_customer has not been called yet - identity not verified (prerequisite gate)."

    if tool_input.get("customer_id") != verified_customer_id:
        return False, "BLOCKED: customer_id does not match the verified customer (prerequisite gate)."

    # Rule B - threshold gate (Task 1.5): amount too high for auto-approval.
    if tool_input.get("amount", 0) > REFUND_THRESHOLD:
        return False, f"BLOCKED: amount exceeds auto-approval threshold of ${REFUND_THRESHOLD} (PreToolUse hook)."

    return True, None


def print_handoff_summary(customer_id: str, amount: float, reason: str) -> None:
    # Task 1.4: structured handoff summary for a human agent who has no
    # access to this conversation transcript.
    print("\n[HANDOFF SUMMARY - escalated to human agent]")
    print(f"  customer_id: {customer_id}")
    print(f"  requested_amount: ${amount}")
    print(f"  root_cause: {reason}")
    print("  recommended_action: Manual review required before refund can be approved.\n")


def run_governed_agent(user_message: str) -> list:
    messages = [{"role": "user", "content": user_message}]
    verified_customer_id = None  # state used by the prerequisite gate (Rule A)

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )
        print(f"\n[Complete Response] -> {response}")
        print(f"\n[stop_reason] -> {response.stop_reason}")
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"\nAgent's final reply: {block.text}")
            break

        if response.stop_reason == "tool_use":
            tool_result_blocks = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                print(f"[tool_use] name={block.name}, input={block.input}")

                # --- PreToolUse hook runs BEFORE we execute anything ---
                allowed, block_reason = pre_tool_use_gate(block.name, block.input, verified_customer_id)

                if not allowed:
                    print(f"[PreToolUse hook] {block_reason}")
                    print_handoff_summary(block.input.get("customer_id", "unknown"), block.input.get("amount", 0), block_reason)
                    result = {"status": "blocked", "reason": block_reason, "escalated_to_human": True}
                else:
                    if block.name == "get_customer":
                        raw_result = get_customer(**block.input)
                        # --- PostToolUse hook runs AFTER execution, BEFORE Claude sees it ---
                        result = post_tool_use_normalize(block.name, raw_result)
                        if "customer_id" in result:
                            verified_customer_id = result["customer_id"]  # unlocks the gate for later refund calls
                    elif block.name == "process_refund":
                        result = process_refund(**block.input)
                    else:
                        result = {"error": "unknown tool"}

                print(f"[tool_result] -> {result}")

                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )

            messages.append({"role": "user", "content": tool_result_blocks})

    return messages


def _json_default(o):
    # Assistant messages contain SDK objects (e.g. ToolUseBlock) that aren't
    # plain dicts - model_dump() converts them so json.dump can serialize them.
    if hasattr(o, "model_dump"):
        return o.model_dump()
    return str(o)


def save_session(messages: list, path: str = SESSION_FILE) -> None:
    # Task 1.7: this is literally what session persistence is under the hood -
    # the message history serialized to disk so it can be reloaded later.
    with open(path, "w") as f:
        json.dump(messages, f, default=_json_default, indent=2)
    print(f"\n[Session saved] -> {path}")


def load_session(path: str = SESSION_FILE) -> list:
    with open(path) as f:
        loaded = json.load(f)
    print(f"[Session loaded] -> {path} ({len(loaded)} messages restored, no new API call needed)")
    return loaded


if __name__ == "__main__":
    print("=== Scenario 1: normal refund (should be allowed) ===")
    messages_1 = run_governed_agent("My email is ali@example.com. I'd like a $200 refund please.")

    print("\n=== Scenario 2: refund above threshold (should be blocked) ===")
    run_governed_agent("My email is sara@example.com. I'd like an $800 refund please.")

    print("\n=== Task 1.7 demo: save & resume a session (no extra API call) ===")
    save_session(messages_1)
    load_session()
