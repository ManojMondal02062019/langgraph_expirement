from agent_state import AgentState
from llm_model import llm, agent
from prompts import command_pre_service_prompt, command_join_validation_error_prompt, summary_prompt
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command
from command_execution_tools import execute_aws_command
from langchain_core.runnables.config import RunnableConfig


def runcommand_agent(state: AgentState) -> AgentState:
    print(f"RUN - RunCommand: State Message: {str(state)}")

    config_values={"command": state["aws_service_attr"], "values": state["aws_service_values"]}    
    #my_config= RunnableConfig(
    #    "configurable"= config_values, 
    #    "tags"=["command_execution_tool"],
    #    "metadata"={"source": "agentstate"}
    #)

    my_config={"configurable": config_values}
    output = execute_aws_command.invoke("Run this command",config=my_config)
    
    #TODO: if output is error, then we might have to take user input
    #else complete it.
    response_messages = []
    response_messages.append(AIMessage(content=str(output)))
    
    state["messages"] = response_messages
    return state