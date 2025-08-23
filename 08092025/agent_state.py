from typing import Annotated, List, TypedDict, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.agents import AgentAction
from aws_service_attributes import AWSServiceAttributes
import operator

# This shared GraphState ensures that every node can read/write from the same context.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    agent_history: Annotated[Sequence[BaseMessage], operator.add]
    llm_output: str
    decision: str
    intent_decision: str
    thread_id: str
    aws_service_attr: Optional[AWSServiceAttributes]
    final_output: Optional[str]
    resume_status: str
    decision_message: str
    decision_option: str    
    interrupt_flag: bool
    #aws_service_values: Dict[str, str]