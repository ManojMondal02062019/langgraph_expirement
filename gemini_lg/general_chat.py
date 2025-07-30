from sharedstate import GraphState
from llm_model import invoke_llm_chat

def chat_agent(state: GraphState) -> GraphState:
    try:
        response = invoke_llm_chat(state["messages"])
    except Exception as e:
        response = AIMessage(content=f"Failed to generate chat response: {e}")
    return {"messages": state["messages"] + [response]}