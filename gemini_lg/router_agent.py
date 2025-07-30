from sharedstate import GraphState
from llm_model import invoke_llm_prompts, invoke_llm_chat
from prompts import router_prompt
from langchain_core.messages import HumanMessage, SystemMessage

def route(state: GraphState) -> str:
    last_user_msg = state["messages"][-1].content
    try:
        classification = invoke_llm_prompts([
            HumanMessage(content=router_prompt),
            HumanMessage(content=last_user_msg)
        ])
        route_decision = classification.content.strip().lower()
        if route_decision not in ["identifyservice_agent", "chat_agent"]:
            route_decision = "chat_agent"
        return route_decision
    except Exception as e:
        print(f"Routing failed: {e}. Defaulting to 'chat_agent'")
        return "chat_agent"