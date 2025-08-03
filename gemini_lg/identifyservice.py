from sharedstate import GraphState
from llm_model import invoke_llm_prompts, invoke_llm_chat
from prompts import system_prompt, identifyservice_prompt
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def identifyservice_agent(state: GraphState) -> GraphState:
    print(f"IdentifyService: State Message: {state["messages"]}")
    user_msg = state["messages"][-1].content
    print(f"IdentifyService: User Message: {user_msg}")

    try:
        intent = invoke_llm_prompts(system_prompt,user_msg)
        print(f"IdentifyService: Intent : {intent.content}")
    except Exception as e:
        raise
        #return {"messages": state["messages"] + [AIMessage(content=f"Failed to classify the intent: {e}")]}
    
    response_text = "Sorry, I couldn't process your request."

    try:
        if intent.content == "Service_Identifier":
            print("IdentifyService: Service Identifier: Invoke LLM Model")
            response_text = invoke_llm_prompts(identifyservice_prompt, user_msg)
            print(f"IdentifyService : Service Identifier: Response ::: {response_text}")
        elif intent.content == "Params_Collector":
            response_text = "dummy"
        elif intent.content == "Command_Executor":
            print("IdentifyService: Command Executor: Invoke LLM Model")
            response_text = invoke_llm_prompts(identifyservice_prompt, user_msg)
            print(f"IdentifyService : Command Executor: Response ::: {response_text}")
        elif intent.content == "general_question":
            response_text = invoke_llm_chat(user_msg).content

    except Exception as e:
        #response_text = f"Error processing request: {e}"
        raise

    return {"messages": state["messages"] + [AIMessage(content=response_text.content)]}