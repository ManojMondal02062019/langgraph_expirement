from langgraph.types import Command, interrupt
from agent_state import AgentState
from aws_service_attributes import AWSServiceAttributes

def human_feedback(state: AgentState):
    # highlight-next-line
    print("---human_feedback block 1 ---")
    return interrupt("Please review the proposed action ?")
    #human_feedback = interrupt({"review_message": "Please review the proposed action ?"})
    #print(f"---human_feedback--- Returned {human_feedback}")
    #return {"messages": state["messages"] + [human_feedback]}