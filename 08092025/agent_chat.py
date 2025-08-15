from agent_state import AgentState
from llm_model import llm
from langchain_core.messages import AIMessage

def chat_agent(state: AgentState) -> AgentState:
    try:
        response = (llm.invoke(state["messages"][-1].content)).content
        print(f"Inside generic Chat Agent Response .....{response}")
    except Exception as e:
        response = AIMessage(content=f"Failed to generate chat response: {e}")

    current_messages = []
    current_messages.append(AIMessage(content=response))

    return {
        "messages": current_messages,
        "final_output": response,
    }