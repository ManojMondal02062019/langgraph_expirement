from agent_state import AgentState
from llm_model import *
from prompts import identify_service_prompt_1 
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks import adispatch_custom_event
from langgraph.types import interrupt, Command
from aws_service_attributes import AWSServiceAttributes
import json
import random
from utils import cleanJson
from langchain_core.messages.utils import filter_messages

#graph.update_state(config, {"name": "LangGraph (library)"})
#https://langchain-ai.github.io/langgraph/tutorials/get-started/5-customize-state/#5-manually-update-the-state

def identifyservice_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    random_number = random.randint(1, 7)
    human_messages = filter_messages(state["messages"], include_types=["human"])
    last_user_msg = ""
    llm_mode = state.get("llm_mode")
    if (len(human_messages) > 0):
        last_user_msg = (human_messages[(len(human_messages))-1]).content

    print(f"IdentifyService: User Message: {last_user_msg}")
    response_text = "Sorry, I couldn't process your request."
    identify_service_prompt = identify_service_prompt_1.replace("#human_message#", last_user_msg)
    final_llm = llm

    if llm_mode is not None and llm_mode == "moderate":
        identify_service_prompt = "User wants a different response then previous one. " + \
                                    "Try giving a response with less parameters." + \
                                    identify_service_prompt
        print(f"+++++++++ Prompt :: {identify_service_prompt}")
        if random_number % 2 == 0:
            final_llm = llm_balanced
            print("+++++++++ 1")
        else:
            print("+++++++++ 2")
            final_llm = llm_enhanced
    messages = [
        ("system", identify_service_prompt),
        ("human", last_user_msg),
    ]
    response_text = final_llm.invoke(messages)
    response_text = cleanJson(response_text.content)
    response_text = json.loads(response_text)
    print(f"IdentifyService: response : {response_text}")
    response_messages = []
    response_messages.append(AIMessage(content=str(response_text)))

    return {
        "messages": response_messages,
        "aws_service_attr": response_text,
        "llm_mode": None
    }