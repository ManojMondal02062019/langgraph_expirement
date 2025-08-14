from agent_state import AgentState
from llm_model import llm, agent
from prompts import identify_service_prompt
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.callbacks import adispatch_custom_event
from langgraph.types import interrupt, Command
from aws_service_attributes import AWSServiceAttributes
import json

#graph.update_state(config, {"name": "LangGraph (library)"})
#https://langchain-ai.github.io/langgraph/tutorials/get-started/5-customize-state/#5-manually-update-the-state

def identifyservice_agent(state: AgentState, config: RunnableConfig) -> AgentState:
    print(f"=========S========= IdentifyService: State Message: {state["messages"]}")
    thread_id = config["configurable"].get("thread_id")
    print(f"Executing node for thread_id 000: {thread_id}")
    user_msg = state["messages"][0].content
    print(f"IdentifyService: User Message: {user_msg}")
    response_text = "Sorry, I couldn't process your request."

    messages = [
        ("system", identify_service_prompt),
        ("human", user_msg),
    ]        
    response_text = llm.invoke(messages)
    json_resp = response_text.content
    json_resp = json_resp.replace("```json", "")
    json_resp = json_resp.replace("```", "")
    #response = f"Please confirm the service and action ? \n\n {json_resp}"
    response = json_resp
    data_dict = json.loads(json_resp)
    data_dict['intent'] = False
    state["aws_service_attr"] = data_dict
    #print(f"IdentifyService: AWS Service Attribute : {state["aws_service_attr"]}")
    #print(f"IdentifyService: Returning Data :: {state['messages']} :: and :: {response}")    
    #ai_message = AIMessage(content=response)
    #state["messages"].append([AIMessage(content=response)])
    #print(f"========E========== IdentifyService: State Message: {state["messages"]}")

    #return {
    #    "messages": [HumanMessage(content=result["output"], name=name),
    #    "resolution": True,
    #    additional_kwargs={"intermediate_steps": result["intermediate_steps"]})]
    #}
    # current_messages = state["messages"]
    #    current_messages.append(HumanMessage(content="Hello from first agent!"))
    #return {
    #    "messages": current_messages,
    #    "my_custom_value": updated_custom_value
    #}

    current_messages = state["messages"]
    current_messages.append(AIMessage(content=response))
    print(f"=========SSSSsssssss========= IdentifyService: State Message: {current_messages}")

    return {
        "messages": current_messages,
        "aws_service_attr": data_dict,
        "final_output": data_dict,
        "llm_output": False
    }
    