from openai import OpenAI 
 
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
# zero shot prompting is when we directly giving the instruction to the model without prior example
SYSTEM_PROMPT = "you are a doctor only reply to the health related querry. if querry is not related to health replly sorry i can help you in this field"
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"system"    ,   "content":SYSTEM_PROMPT},
        {"role": "user"     ,   "content": "my name is ashvini,and i need to help in football"}
    ]   
)

print(response.choices[0].message.content)
