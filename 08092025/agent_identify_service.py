from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks import adispatch_custom_event
from langgraph.types import interrupt, Command
from aws_service_attributes import AWSServiceAttributes
import json


def identifyservice_agent(state: AgentState) -> AgentState:
    print(f"IdentifyService: State Message: {state["messages"]}")
    user_msg = state["messages"][0].content
    print(f"IdentifyService: User Message: {user_msg}")
    response_text = "Sorry, I couldn't process your request."

    try:
        messages = [
            ("system", identify_service_prompt),
            ("human", user_msg),
        ]        
        response_text = llm.invoke(messages)
        json_resp = response_text.content
        json_resp = json_resp.replace("```json", "")
        json_resp = json_resp.replace("```", "")
        response = f"Please confirm the service and action ? \n\n {json_resp}"
        data_dict = json.loads(json_resp)
        data_dict['intent'] = False
        state["aws_service_attr"] = data_dict
        print(f"IdentifyService: AWS Service Attribute : {state["aws_service_attr"]}")
        print(f"IdentifyService: Returning Data :: {state['messages']} :: and :: {response}")
    except Exception as e:
        #response_text = f"Error processing request: {e}" 
        raise e
    return {"messages": state["messages"] + [AIMessage(content=response)]}