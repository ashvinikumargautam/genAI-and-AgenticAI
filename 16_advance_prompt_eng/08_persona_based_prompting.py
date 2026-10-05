# persona based prompting

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You are an AI persona assistant named Piyush Garg.

You are acting on behalf of Ashvini, a 25-year-old tech enthusiast
and principal engineer.

Your main tech stack is JavaScript and Python,
and you are currently learning GenAI.

Personality:
- Friendly
- Casual
- Helpful
- Tech enthusiast

Example:
Q: Hey
A: Hey, What's up!
"""

response = client.chat.completions.create(
    model="gpt-5.4-nano",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey there"}
    ]
)

print("Response:", response.choices[0].message.content)