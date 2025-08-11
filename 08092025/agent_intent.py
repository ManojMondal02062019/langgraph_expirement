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
        response_text = llm.invoke(messages)
        print(f"Intent Agent: Response : {response_text}")
    except Exception as e:
        response_text = f"Error processing request: {e}"

    return {"messages": state["messages"] + [AIMessage(content=response_text.content)]}