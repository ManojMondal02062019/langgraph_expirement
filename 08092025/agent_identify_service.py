from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt_1 
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks import adispatch_custom_event
from langgraph.types import interrupt, Command
from aws_service_attributes import AWSServiceAttributes
import json
from utils import cleanJson
from langchain_core.messages.utils import filter_messages

#graph.update_state(config, {"name": "LangGraph (library)"})
#https://langchain-ai.github.io/langgraph/tutorials/get-started/5-customize-state/#5-manually-update-the-state

def identifyservice_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    human_messages = filter_messages(state["messages"], include_types=["human"])
    last_user_msg = ""
    if (len(human_messages) > 0):
        last_user_msg = (human_messages[(len(human_messages))-1]).content

    print(f"IdentifyService: User Message: {last_user_msg}")
    response_text = "Sorry, I couldn't process your request."
    identify_service_prompt = identify_service_prompt_1.replace("#human_message#", last_user_msg)

    messages = [
        ("system", identify_service_prompt),
        ("human", last_user_msg),
    ]        
    response_text = llm.invoke(messages)
    response_text = cleanJson(response_text.content)
    response_text = json.loads(response_text)
    print(f"IdentifyService: response : {response_text}")
    response_messages = []
    response_messages.append(AIMessage(content=str(response_text)))

    return {
        "messages": response_messages,
        "aws_service_attr": response_text,
    }