from sharedstate import GraphState
from llm_model import invoke_llm_prompts, invoke_llm_chat
from prompts import router_prompt
from langchain_core.messages import HumanMessage, SystemMessage

def route(state: GraphState) -> str:
    last_user_msg = state["messages"][-1].content
    print(f"RouterAgent: last_user_msg: {last_user_msg}")
    try:
        classification = invoke_llm_prompts(router_prompt, last_user_msg)
        print(f"RouterAgent: Classification ::: {classification}")
        route_decision = classification.content.strip().lower()
        print(f"RouterAgent: Route Decision :: {route_decision}")
        if route_decision not in ["identifyservice_agent", "chat_agent", "aws_agent"]:
            route_decision = "chat_agent"
        return route_decision
    except Exception as e:
        print(f"Routing failed again : {e}. Defaulting to 'chat_agent'")
        return "chat_agent"
    