from agent_state import AgentState
from llm_model import llm

def chat_agent(state: AgentState) -> AgentState:
    try:
        response = llm.invoke(state["messages"])
    except Exception as e:
        response = AIMessage(content=f"Failed to generate chat response: {e}")
    return {"messages": state["messages"] + [response]}