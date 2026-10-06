from openai import OpenAI
from dotenv import load_dotenv
import requests
import json


# ============================================================
# SETUP
# ============================================================

load_dotenv()

client = OpenAI()


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert AI weather assistant.

You work in four stages:

1. START
2. PLAN
3. TOOL
4. OUTPUT

Available Tools:
- get_weather: takes a city name as an input string and returns
  current weather information.

For every response, return ONLY valid JSON.

Normal format:

{
    "step": "START" | "PLAN" | "OUTPUT",
    "content": "string"
}

TOOL format:

{
    "step": "TOOL",
    "tool": "get_weather",
    "input": "city name",
    "content": "short description"
}

Rules:

- START:
  Understand and acknowledge the user's request.

- PLAN:
  Briefly describe what needs to be done.
  Do not reveal private chain-of-thought.

- TOOL:
  Use get_weather when current weather information is required.
  The "tool" field must contain the tool name.
  The "input" field must contain only the city name.

- OUTPUT:
  Use the weather information returned by the tool.
  The "content" field must contain the final answer in
  normal natural-language text.

- Never invent or guess current weather information.

- If the user does not provide a city, ask for the city.

- For current weather questions, always use get_weather.

- Perform only ONE stage at a time.

- After receiving the tool result, return OUTPUT.

- Do not mention internal stages, tools, JSON, or planning
  in the final OUTPUT.

Example:

User:
What is the weather in Delhi?

Assistant:
{
    "step": "START",
    "content": "The user wants the current weather in Delhi."
}

Assistant:
{
    "step": "PLAN",
    "content": "I need to retrieve the current weather for Delhi."
}

Assistant:
{
    "step": "TOOL",
    "tool": "get_weather",
    "input": "Delhi",
    "content": "Retrieving the current weather for Delhi."
}

Tool:
"The weather in Delhi is Sunny +32°C"

Assistant:
{
    "step": "OUTPUT",
    "content": "The current weather in Delhi is sunny and 32°C."
}

Example:

User:
What's the weather?

Assistant:
{
    "step": "START",
    "content": "The user wants current weather information but has not specified a city."
}

Assistant:
{
    "step": "OUTPUT",
    "content": "Sure! Which city would you like the weather for?"
}
"""


# ============================================================
# WEATHER TOOL
# ============================================================

def get_weather(city: str):

    url = f"https://wttr.in/{city}?format=%C+%t"

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 200:

            weather = response.text.strip()

            return f"The weather in {city} is {weather}"

        return "Unable to retrieve weather information."

    except requests.RequestException as e:

        return f"Weather service error: {e}"


# ============================================================
# AVAILABLE TOOLS
# ============================================================

available_tools = {
    "get_weather": get_weather
}


# ============================================================
# MESSAGE HISTORY
# ============================================================

message_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


# ============================================================
# CHAT LOOP
# ============================================================

print("\nWeather AI Assistant")
print("====================")
print("Type 'exit' to quit.\n")


while True:

    # --------------------------------------------------------
    # Get user input
    # --------------------------------------------------------

    user_query = input("You: ").strip()

    if user_query.lower() in ["exit", "quit"]:

        print("\nGoodbye!")
        break

    if not user_query:

        continue

    message_history.append(
        {
            "role": "user",
            "content": user_query
        }
    )


    # ========================================================
    # AGENT LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # Ask LLM
        # ----------------------------------------------------

        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            response_format={
                "type": "json_object"
            },
            messages=message_history
        )


        raw_result = response.choices[0].message.content


        # ----------------------------------------------------
        # Store assistant response
        # ----------------------------------------------------

        message_history.append(
            {
                "role": "assistant",
                "content": raw_result
            }
        )


        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:

            parsed_result = json.loads(raw_result)

        except json.JSONDecodeError:

            print("\nError: Model returned invalid JSON.")
            print(raw_result)
            break


        # ----------------------------------------------------
        # Get stage
        # ----------------------------------------------------

        step = parsed_result.get("step")
        content = parsed_result.get("content")


        # ====================================================
        # START
        # ====================================================

        if step == "START":

            print("\nSTART:", content)


        # ====================================================
        # PLAN
        # ====================================================

        elif step == "PLAN":

            print("PLAN:", content)


        # ====================================================
        # TOOL
        # ====================================================

        elif step == "TOOL":

            tool_name = parsed_result.get("tool")
            tool_input = parsed_result.get("input")


            print("TOOL:", tool_name)
            print("INPUT:", tool_input)


            # ------------------------------------------------
            # Check tool
            # ------------------------------------------------

            if tool_name not in available_tools:

                print("Unknown tool:", tool_name)
                break


            # ------------------------------------------------
            # Get Python function
            # ------------------------------------------------

            tool_function = available_tools[tool_name]


            # ------------------------------------------------
            # Execute tool
            # ------------------------------------------------

            tool_result = tool_function(tool_input)


            print("TOOL RESULT:", tool_result)


            # ------------------------------------------------
            # Send tool result back to LLM
            # ------------------------------------------------

            message_history.append(
                {
                    "role": "user",
                    "content": f"""
The tool returned this result:

{tool_result}

Use this tool result to answer the user's original question.

Return the OUTPUT stage now.
"""
                }
            )


        # ====================================================
        # OUTPUT
        # ====================================================

        elif step == "OUTPUT":

            print("\nAssistant:", content)
            print()

            break


        # ====================================================
        # UNKNOWN STEP
        # ====================================================

        else:

            print("\nUnknown step:", step)
            break