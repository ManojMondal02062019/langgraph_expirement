from agent_state import AgentState
from llm_model import llm, agent, llm_with_tools
from prompts import command_pre_service_prompt, command_join_validation_error_prompt, summary_prompt
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command


def runcommand_agent(state: AgentState) -> AgentState:
    print(f"RUN - RunCommand: State Message: {state["messages"]}")
    
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)

    print(f"RUN - RunCommand: Response : {response}")
    response_messages = []
    response_messages.append(AIMessage(content=str(response)))

    return {
        "messages": response_messages,
        "interrupt_flag": True,
    }