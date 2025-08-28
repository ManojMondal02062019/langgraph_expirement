from agent_state import AgentState
from llm_model import llm, agent
from prompts import command_pre_service_prompt, command_join_validation_error_prompt, summary_prompt
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command
from command_execution_tools import execute_aws_command


def runcommand_agent(state: AgentState) -> AgentState:
    print(f"RUN - RunCommand: State Message: {state["messages"]}")

    #manual invoke tool
    output = execute_aws_command.invoke(config={"configurable": {"state": state}})
    
    #TODO: if output is error, then we might have to take user input
    #else complete it.
    
    return {
        "messages": str(output),
        "interrupt_flag": False,
    }