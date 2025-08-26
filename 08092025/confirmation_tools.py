from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from agent_state import AgentState
from typing import Annotated

@tool
def executeAWSCommandTool(command_to_run: str, state: Annotated[AgentState, InjectedState]) -> str:
    """Execute the command received """
    
    state_messages = state.get("messages", {})
    print(f"Tool :: executeAWSCommandTool :: {state_messages}")
    return "Hello Tool"