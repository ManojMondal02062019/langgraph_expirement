from agent_state import AgentState
from llm_model import llm
from prompts import router_prompt
from langchain_core.messages import HumanMessage, SystemMessage

def route(state: AgentState) -> str:
    last_user_msg = state["messages"][-1].content
    print(f"RouterAgent: last_user_msg: {last_user_msg}")
    try:
        classification = llm.invoke([HumanMessage(content=router_prompt), HumanMessage(content=last_user_msg)])
        print(f"RouterAgent: Classification ::: {classification}")
        route_decision = classification.content.strip().lower()
        print(f"RouterAgent: Route Decision :: {route_decision}")
        if route_decision not in ["intent_agent", "chat_agent"]:
            print(f"RouterAgent: Route Decision Overridden")
            route_decision = "chat_agent"
        
        return route_decision
    except Exception as e:
        print(f"Routing failed again : {e}. Defaulting to 'chat_agent'")
        return "chat_agent"
    