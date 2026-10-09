from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
from typing import Optional,Literal
from langgraph.graph import StateGraph, START,END
from openai import OpenAI

client = OpenAI()

class State(TypedDict):
    user_query : str
    llm_output : Optional[str]
    is_good : Optional[bool]

def chatbot(state:State):
    print("chatbot node : ", state)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user","content":state.get("user_query")}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

def evaluate_response(state : State) -> Literal["chatbot_gemini" , "endnode"]:
    print("evaluate_response node : ",state)
    if False:
        return "endnode"
    return "chatbot_gemini"

def chatbot_gemini(state : State):
    print("chatbot_gemini node : ",state)
    response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role":"user","content":state.get("user_query")}
            ]
        )
    state["llm_output"] = response.choices[0].message.content
    return state

def endnode(state: State):
    print("end_node node : ",state)
    
    return state
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
# graph_builder.add_node("evaluate_response",evaluate_response)
graph_builder.add_node("chatbot_gemini",chatbot_gemini)
graph_builder.add_node("endnode",endnode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_conditional_edges("chatbot",evaluate_response)  # node
graph_builder.add_edge("chatbot_gemini","endnode")
graph_builder.add_edge("endnode",END)

graph = graph_builder.compile()
updated_state = graph.invoke(State({"user_query": "Hey what is 2+2 ?"}))
print("\n\nupdated_State : " , updated_state)


#              START
#                │
#                ▼
#           ┌─────────┐
#           │ chatbot │
#           └────┬────┘
#                │
#                ▼
#       evaluate_response
#           /          \
#          /            \
#         ▼              ▼
# chatbot_gemini       endnode
#         │              │
#         ▼              ▼
#       endnode         END
#         │
#         ▼
#        END