from langgraph.types import Command, interrupt
from typing import Literal
from agent_state import AgentState
from aws_service_attributes import AWSServiceAttributes
from typing_extensions import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langchain_core.runnables.config import RunnableConfig


def human_feedback(state: AgentState, config: RunnableConfig) -> AgentState:
    # highlight-next-line
    print("---human_feedback block---")
    print(f" AGENT STATE ===== {state}")
    identify_service_response = state["aws_service_attr"]
    print(f"Service Response :: {identify_service_response}")
    value = interrupt({"review_message": "Please review the response"})
    return state

# Human approval node
def human_approval(state: AgentState, config: RunnableConfig) -> Command[Literal["approved_intent_path", "rejected_intent_path", "modify_intent_path"]]:

    # Generate the human approval message
    approval_message = f"Kindly confirm to proceed OR you can modify your query ?"

    # Pause the graph and surface the approval message
    decision = interrupt({"message": approval_message})    
    #decision = interrupt({
    #    "question": "Do you approve, reject the following output? OR you want to modify the request",
    #    "llm_output": state["llm_output"]
    #})

    if decision == "approve":
        print(f" DECISION APPROVED .... {decision}")
        return Command(goto="approved_intent_path", update={"decision": "approved"})
    elif decision == "reject":
        print(f" DECISION REJECTED .... {decision}")
        return Command(goto="rejected_intent_path", update={"decision": "rejected"})
    else:
        print(f" DECISION MODIFY .... {decision}")
        return Command(goto="modify_intent_path", update={"decision": "modify"})


# Next steps after approval
def approved_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Approved path taken......1")

    return state

# Alternative path after rejection
def rejected_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Rejected path taken...2")
    return state

# Alternative path after rejection
def modify_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Rejected path taken.")
    return state