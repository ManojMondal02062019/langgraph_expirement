from agent_state import AgentState
from llm_model import llm, agent
from prompts import *
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command
from command_execution_tools import execute_aws_command
from langchain_core.runnables.config import RunnableConfig
import json
import ast

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
    response_messages = []
    response_messages.append(AIMessage(content=str(output)))
    
    state["aws_command_output"] = output
    state["messages"] = response_messages
    state["aws_command_status"] = "failed"
    return state

def post_commandexecute_agent(state: AgentState) -> AgentState:
    print(f"PostCommandExecute, state: {state}")
    print(f"PostCommandExecute, Command Output: {state["aws_command_output"]}")
    if "error" not in (state["aws_command_output"]).lower():
        msg_content = state["aws_command_output"] + "\n\nThankyou. You can start again with a new search."
        state["messages"].append(AIMessage(content=msg_content))
        state["aws_command_status"] = "success"
        print("PostCommandExecute, We are good to end the workflow.")
    else:
        aws_command_output = state["messages"][-1].content
        # let's invoke the llm to find out the issue.
        aws_values = state["aws_service_values"]
        aws_command = state["aws_service_attr"]

        #build the prompt and get the missing information
        prompt = command_post_service_prompt.replace("#aws_values#", str(aws_values))
        prompt = prompt.replace("#aws_command#", str(aws_command))
        messages = [
            ("system", prompt),
            ("human", str(aws_command_output)),
        ]
        response_text = llm.invoke(messages).content
        response_text = cleanJson(response_text)
        
        #ask the user on the missing
        value = interrupt({
            "text_to_review": f"{aws_command_output}.  {response_text}  Please fix the issue and try again or type in 'exit' to search new"
        })
        print(f"PostCommandExecute, User Response received: {value}")
        if value.lower() == "exit" or value.lower() == "bye":
            ai_message = []
            ai_message.append(AIMessage(content="Thankyou. You can perform search again"))
            state["messages"] = ai_message
            state["aws_command_status"] = ""
            return state
        print(f"PostCommandExecute, Old Response : {response_text}")

        prompt = override_aws_values_prompt.replace("#aws_service_values#", str(state["aws_service_values"]))
        new_params = f"Old Parameter and value is {response_text}, New Value received is {value}"
        messages = [
            ("system", prompt),
            ("human", new_params),
        ]
        response_text = llm.invoke(messages).content
        response_text = cleanJson(response_text.strip())
        # convert it into dict
        if isinstance(response_text, str):      
            try:
                response_text = json.loads(response_text)
            except Exception as e:
                print(e)
        
        print(f"PostCommandExecute, User Response received To check Parameter Key and Value: {response_text}")
        
        human_message = []
        human_message.append(HumanMessage(content=value))
        state["messages"] = human_message
        state["aws_service_values"] = response_text
        state["aws_command_status"] = "failed"
    return state