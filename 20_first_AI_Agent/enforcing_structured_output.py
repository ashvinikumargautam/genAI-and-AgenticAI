from openai import OpenAI
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from typing import Optional
import os


load_dotenv()
client = OpenAI()


SYSTEM_PROMPT = """
You are an expert AI assistant.

You work in four stages:
1. START
2. PLAN
3. TOOL
4. OUTPUT

Available Tools:
- get_weather(city): gets current weather information.
- run_command(cmd): executes a Windows PowerShell command.
- create_folder(folder_path): creates a folder.
- create_file(file_path, content): creates a file and writes content into it.

Rules:

- START: Understand and acknowledge the user's request.
- PLAN: Briefly describe what needs to be done.
- TOOL: Use the appropriate tool.
- OUTPUT: Give the final answer after completing the requested action.

Weather:
- For current weather questions, always use get_weather.
- For get_weather, input must contain only the city name.
- Never invent current weather information.
- If no city is provided, ask for the city.

Windows:
- The user's system is Windows.
- Always use Windows-compatible commands.
- Never use Linux commands such as ls, cat, mv, rm, find, or mkdir -p.

File creation:
- Use create_folder when a folder needs to be created.
- Use create_file when a file needs to be created.
- create_file requires both a file path and the complete file content.
- If the user asks for multiple files, create each file with its complete content.
- Do not use run_command to create files when create_file can be used.
- Preserve the requested file extensions.
- Put the actual code/content inside the content field.
- Do not put explanations inside the file content unless the user asks for them.

Stage rules:
- Perform only ONE stage at a time.
- After START, return PLAN.
- After PLAN, return TOOL.
- After receiving the tool result, return OUTPUT.
- Do not reveal private chain-of-thought.
- Do not mention internal stages, JSON, or tools in the final OUTPUT.
"""


def run_command(cmd: str):
    try:
        result = os.popen(cmd).read()
        return result.strip()
    except Exception as e:
        return f"Command error: {e}"


def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return f"The weather in {city} is {response.text.strip()}"

        return "Unable to retrieve weather information."

    except requests.RequestException as e:
        return f"Weather service error: {e}"


def create_folder(folder_path: str):
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder created successfully: {folder_path}"

    except Exception as e:
        return f"Error creating folder: {e}"


def create_file(file_path: str, content: str):
    try:

        folder = os.path.dirname(file_path)

        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        return f"File created successfully: {file_path}"

    except Exception as e:
        return f"Error creating file: {e}"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_folder": create_folder,
    "create_file": create_file
}


class MyOutputFormat(BaseModel):

    step: str = Field(
        ...,
        description="START, PLAN, TOOL or OUTPUT"
    )

    content: Optional[str] = Field(
        None,
        description="Content for the step"
    )

    tool: Optional[str] = Field(
        None,
        description="Tool name"
    )

    input: Optional[str] = Field(
        None,
        description="Tool input"
    )

    file_path: Optional[str] = Field(
        None,
        description="File path when using create_file"
    )

    file_content: Optional[str] = Field(
        None,
        description="Complete content to write into the file"
    )


message_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


print("\nAI Assistant")
print("====================")
print("Type 'exit' to quit.\n")


while True:

    user_query = input("You: ").strip()

    if user_query.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        break

    if not user_query:
        continue

    message_history.append({
        "role": "user",
        "content": user_query
    })

    while True:

        response = client.chat.completions.parse(
            model="gpt-5.4-nano",
            response_format=MyOutputFormat,
            messages=message_history
        )

        parsed_result = response.choices[0].message.parsed

        if parsed_result is None:
            print("Error: No structured output.")
            break

        message_history.append({
            "role": "assistant",
            "content": parsed_result.model_dump_json()
        })

        step = parsed_result.step
        content = parsed_result.content

        if step == "START":

            print("\nSTART:", content)

        elif step == "PLAN":

            print("PLAN:", content)

        elif step == "TOOL":

            tool_name = parsed_result.tool

            print("TOOL:", tool_name)

            if tool_name not in available_tools:
                print("Unknown tool:", tool_name)
                break


            # ---------------------------------
            # GET WEATHER
            # ---------------------------------

            if tool_name == "get_weather":

                tool_input = parsed_result.input

                if not tool_input:
                    print("Tool input is missing.")
                    break

                print("INPUT:", tool_input)

                tool_result = get_weather(tool_input)

                print("TOOL RESULT:", tool_result)


            # ---------------------------------
            # RUN COMMAND
            # ---------------------------------

            elif tool_name == "run_command":

                tool_input = parsed_result.input

                if not tool_input:
                    print("Tool input is missing.")
                    break

                print("INPUT:", tool_input)

                tool_result = run_command(tool_input)

                print("TOOL RESULT:", tool_result)


            # ---------------------------------
            # CREATE FOLDER
            # ---------------------------------

            elif tool_name == "create_folder":

                tool_input = parsed_result.input

                if not tool_input:
                    print("Folder path is missing.")
                    break

                print("FOLDER:", tool_input)

                tool_result = create_folder(tool_input)

                print("TOOL RESULT:", tool_result)


            # ---------------------------------
            # CREATE FILE
            # ---------------------------------

            elif tool_name == "create_file":

                file_path = parsed_result.file_path
                file_content = parsed_result.file_content

                if not file_path:
                    print("File path is missing.")
                    break

                if file_content is None:
                    print("File content is missing.")
                    break

                print("FILE:", file_path)
                print("Creating file...")

                tool_result = create_file(
                    file_path,
                    file_content
                )

                print("TOOL RESULT:", tool_result)


            # ---------------------------------
            # SEND TOOL RESULT BACK TO MODEL
            # ---------------------------------

            message_history.append({
                "role": "user",
                "content": f"""
The tool returned this result:

{tool_result}

Use this result to answer the user's original question.
Return the OUTPUT stage now.
"""
            })


        elif step == "OUTPUT":

            print("\nAssistant:", content, "\n")
            break


        else:

            print("Unknown step:", step)
            break