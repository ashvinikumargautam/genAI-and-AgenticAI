from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You are an expert AI assistant.

You work in three stages:

1. START
2. PLAN
3. OUTPUT

Rules:
- Return ONLY valid JSON.
- Use exactly this format:

{
    "step": "START" | "PLAN" | "OUTPUT",
    "content": "string"
}

- START: acknowledge and understand the user's request.
- PLAN: provide concise, high-level reasoning steps. Do not reveal private chain-of-thought.
- OUTPUT: provide the final answer.
- Perform only one stage at a time.
- Multiple PLAN stages are allowed.
- After planning is complete, return OUTPUT.
"""

print("\n\n")

message_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

user_query = input("Please enter your query: ")

message_history.append(
    {
        "role": "user",
        "content": user_query
    }
)

while True:

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_result = response.choices[0].message.content

    # print("\nRAW:", raw_result)

    message_history.append(
        {
            "role": "assistant",
            "content": raw_result
        }
    )

    parsed_result = json.loads(raw_result)

    step = parsed_result.get("step")
    content = parsed_result.get("content")

    if step == "START":
        print("START:", content)

    elif step == "PLAN":
        print("PLANNING:", content)

    elif step == "OUTPUT":
        print("OUTPUT:", content)
        break

    else:
        print("Unknown step:", step)
        break