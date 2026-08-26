import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
print("Client ", client)

MODEL = "claude-haiku-4-5-20251001"


def get_weather(city: str) -> str:
    fake_data = {
        "karachi": "34°C, dhoop tez hai (sunny)",
        "lahore": "38°C, dhundlaya hua (hazy)",
        "islamabad": "29°C, halki barish (light rain)",
    }
    return fake_data.get(city.lower(), f"'{city}' ka data mojood nahi hai.")


tools = [
    {
        "name": "get_weather",
        "description": "Kisi bhi city ka current weather batata hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City ka naam, jaise 'Karachi' ya 'Lahore'",
                }
            },
            "required": ["city"],
        },
    }
]


def run_agentic_loop(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            tools=tools,
            messages=messages,
        )
        print(f"\n[Complete Response] -> {response}")
        print(f"\n[stop_reason] -> {response.stop_reason}")

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"\nClaude ka final jawab: {block.text}")
            break

        if response.stop_reason == "tool_use":
            tool_result_blocks = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"[tool_use] Claude ne mangwaya -> name={block.name}, input={block.input}, tool_use_id={block.id}")

                    if block.name == "get_weather":
                        result = get_weather(**block.input)
                    else:
                        result = "Unknown tool"

                    print(f"[tool_result] Hamare function ka output -> {result}")

                    tool_result_blocks.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            messages.append({"role": "user", "content": tool_result_blocks})
            print(f"\nCOMPLETE MESSAGE OBJECT: {messages}")

if __name__ == "__main__":
    run_agentic_loop("Karachi ka weather kaisa hai abhi?")
