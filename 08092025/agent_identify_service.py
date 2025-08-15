from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks import adispatch_custom_event
from langgraph.types import interrupt, Command
from aws_service_attributes import AWSServiceAttributes
import json
from langchain_core.messages.utils import filter_messages

#graph.update_state(config, {"name": "LangGraph (library)"})
#https://langchain-ai.github.io/langgraph/tutorials/get-started/5-customize-state/#5-manually-update-the-state

def identifyservice_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    user_msg = state["messages"]    
    human_messages = filter_messages(user_msg, include_types=["human"])
    last_user_msg = ""
    total_messages = len(human_messages)
    if (total_messages > 0):
        last_user_msg = (human_messages[total_messages-1]).content

    print(f"---S---IdentifyService: User Message: {last_user_msg}")
    response_text = "Sorry, I couldn't process your request."

    messages = [
        ("system", identify_service_prompt),
        ("human", last_user_msg),
    ]        
    response_text = llm.invoke(messages)
    json_resp = response_text.content
    json_resp = json_resp.replace("```json", "")
    json_resp = json_resp.replace("```", "")
    response = json_resp
    data_dict = json.loads(json_resp)
    data_dict['intent'] = False
    state["aws_service_attr"] = data_dict

    current_messages = []
    current_messages.append(AIMessage(content=response))
    print(f"---E--- IdentifyService: State Message: {current_messages}")

    return {
        "messages": current_messages,
        "aws_service_attr": data_dict,
        "final_output": data_dict,
        "llm_output": False
    }
    