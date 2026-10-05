from openai import OpenAI 
 
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"system"    ,   "content":"you are a doctor only reply to the health related querry. if querry is not related to health replly sorry i can help you in this field"},
        {"role": "user"     ,   "content": "my name is ashvini,and i need to help in football"}
    ]   
)

print(response.choices[0].message.content)
