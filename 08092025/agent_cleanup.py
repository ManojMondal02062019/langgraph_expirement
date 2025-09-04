from agent_state import AgentState
from llm_model import *
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from prompts import summary_prompt

def cleanupcommand_agent(state: AgentState) -> AgentState:
    print(f"CleanUpCommand: State Message Size: {len(state["messages"])}")
    # now we have to summarize the user input
    messages = [
        ("system", summary_prompt),
        ("human", state["messages"]),
    ]        
    response_text = llm.invoke(messages).content
    print(f"Summarized AI Message :: {response_text}")
    #remove all state messages
    messages = state["messages"]
    if len(messages) > 5:
        # remove the earliest two messages
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return {}