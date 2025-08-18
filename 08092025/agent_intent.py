from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt, intent_prompt
from langchain_core.messages import HumanMessage, AIMessage

def intent_agent(state: AgentState) -> AgentState:
    user_msg = state["messages"][-1].content
    print(f"Intent Agent: User_Msg: {user_msg}")

    response_text = "Sorry, I couldn't understand your request."

    try:
        messages = [
            ("system", intent_prompt),
            ("human", user_msg),
        ]
        response_text = llm.invoke(messages).content
    except Exception as e:
        response_text = f"Error processing request: {e}"

    current_messages = []
    current_messages.append(AIMessage(content=response_text))
    print(f"Intent_agent: Response: {response_text}")

    return {
        "messages": current_messages,
        "final_output": ""
    }    