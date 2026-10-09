from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START,END
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

class  State(TypedDict):
    messages : Annotated[list,add_messages]

def chatbot(state:State):
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]}

def samplenode(state : State):
    print("\n\n",{"messages":["sample message appended"]},"\n\n") 
    return {"messages":["sample message appended"]}

# using this graphbuilder variable i can build my graph
graph_builder = StateGraph(State) 
graph_builder.add_node("chatbot" , chatbot)
graph_builder.add_node("samplenode" , samplenode)
# start 
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
# END
graph_builder.add_edge("samplenode", END)

# state = {message : ["hey there"]}
# node runs : chatbot(state: ["hey there"])  --> ["hi this is a message from chatbot node"]
# state = {message : ["hey there","hi this is a message from chatbot node"]}


graph = graph_builder.compile()


updated_state = graph.invoke(State({"messages" : ["Hi my name is ashvini"]}))
print("\n\nupdated_state",updated_state)