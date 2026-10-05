from fastapi import FastAPI,Body
from ollama import Client

app = FastAPI()
client = Client (
    host = "http://localhost:11434"
)

@app.get("/")
def read_root():
    return {"hello" : "world  "}

@app.get("/contact-us")
def read_root():
    return {"email":"ashvini1275@gmail.com"}

@app.post("/chat")
def chat(
        message :str = Body(...,description="the message")
):
    response = client.chat(model = "qwen3:1.7b",messages = [
        {"role" : "user" , "content" : message}
    ])

    return {"response":response.message.content}