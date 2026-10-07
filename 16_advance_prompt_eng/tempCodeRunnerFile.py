from openai import OpenAI 
 
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
# zero shot prompting is when we directly giving the instruction to the model without prior example
SYSTEM_PROMPT = """
you are a doctor only reply to the coding related querry. 
if querry is not related to health replly sorry i can not help you in this field" 
Rule :
    - strictly follow the output in json format
    output format :
        {{
        "code" : "string"or None ,
        "isCodingQuestion" : boolean
        }}
exapmle :
Q: can you explain a+b whole square
A: {{
        "code" : None ,
        "isCodingQuestion" : False
    }}
Q: hey write a code in python for adding two numbers.
A:  {{
        "code" : "def add(a,b):
      return a+b" ,
        "isCodingQuestion" : False
    }}


"""


response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"system"    ,   "content":SYSTEM_PROMPT},
        {"role": "user"     ,   "content": "write the code of find string is palindrome"}
    ]   
)

print(response.choices[0].message.content)
