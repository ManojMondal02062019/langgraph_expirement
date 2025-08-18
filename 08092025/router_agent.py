from agent_state import AgentState
from llm_model import llm
from prompts import router_prompt
from langchain_core.messages import HumanMessage, SystemMessage

def route(state: AgentState) -> str:
    last_user_msg = state["messages"][-1].content
    classification = llm.invoke([HumanMessage(content=router_prompt), HumanMessage(content=last_user_msg)])
    route_decision = classification.content.strip().lower()
    if route_decision not in ["intent_agent", "chat_agent"]:
        route_decision = "chat_agent"
    state["final_output"] = ""
    print(f"RouterAgent: Route Decision {route_decision}")
    return route_decision