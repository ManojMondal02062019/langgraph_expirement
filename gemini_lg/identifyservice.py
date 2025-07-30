from sharedstate.py import GraphState
from llm_model import invoke_llm_prompts, invoke_llm_chat
from prompts import 
from langchain_core.messages import HumanMessage, SystemMessage

def identifyservice_agent(state: GraphState) -> GraphState:
    user_msg = state["messages"][-1].content

    try:
        intent = invoke_llm_prompts([HumanMessage(content=system_prompt), HumanMessage(content=user_msg)]).content.strip()
    except Exception as e:
        return {"messages": state["messages"] + [AIMessage(content=f"Failed to classify the intent: {e}")]}
    
    response_text = "Sorry, I couldn't process your request."

    try:
        if intent == "Service_Identifier":
            response_text = invoke_llm_prompts([HumanMessage(content=identifyservice_prompt), HumanMessage(content=user_msg)]).content.strip()
        elif intent == "Params_Collector":
            response_text = "dummy"
        elif intent == "Command_Executor":
            response_text = "dummy"
        elif intent == "general_question":
            response_text = invoke_llm_chat(user_msg).content

    except Exception as e:
        response_text = f"Error processing request: {e}"

    return {"messages": state["messages"] + [AIMessage(content=response_text)]}

    