from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt
from langchain_core.messages import AIMessage

def commandexecute_agent(state: AgentState) -> AgentState:
    print(f"commandexecute: State Message: {state["messages"]}")
    user_msg = state["messages"][-1].content
    response_text = "Sorry, I couldn't process your request."

    try:
        response_text = llm.invoke(identify_service_prompt,user_msg)
        print(f"CommandExecute: Response : {response_text}")
    except Exception as e:
        response_text = f"Error processing request: {e}" 
    
    return {"messages": state["messages"] + [AIMessage(content=response_text.content)]}