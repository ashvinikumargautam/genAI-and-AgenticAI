from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START,END
from langchain.chat_models import init_chat_model

#new thing
from langgraph.checkpoint.mongodb import MongoDBSaver 
  

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)

class  State(TypedDict):
    messages : Annotated[list,add_messages]

def chatbot(state:State):
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]}


# using this graphbuilder variable i can build my graph
graph_builder = StateGraph(State) 
graph_builder.add_node("chatbot" , chatbot)

# start 
graph_builder.add_edge(START, "chatbot")
# END
graph_builder.add_edge("chatbot", END)


# state = {message : ["hey there"]}
# node runs : chatbot(state: ["hey there"])  --> ["hi this is a message from chatbot node"]
# state = {message : ["hey there","hi this is a message from chatbot node"]}


graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"

with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(
        checkpointer=checkpointer
    )
# thread id is unique for on condidate
    config = {
        "configurable": {
            "thread_id": "piyush"
        }
    }

    for chunk in graph_with_checkpointer.stream(
        State({
            # "messages": ["Hi, my name is ashvini"]
            # "messages": ["what is my name?"]
            # "messages": ["im learning langraph?"]
            "messages": ["what im learning?"]
        }),
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

