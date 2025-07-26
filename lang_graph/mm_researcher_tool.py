from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from mm_llm_model import llm_model
from mm_state import State
from mm_state import AWS_Service, aws_json_schema, json_response_format_response
import json

def generate_research_assistant_prompt(memory: str = "None", prompt: str = "None") -> str:
    return f"""
    You are an agent to provide only the AWS Service Name and action extracted from user prompt {prompt}.
    Only return the Service Name and action. The response should be very concise.
    The output should be as per this example {json_response_format_response}.
    We don't want markdown in our output
    - Output only described JSON output format compatible with python backend.
    - JSON, keys and values require double-quotes

    """

def research_assistant(state: State, config: RunnableConfig):

    # Generate instructions for the assistant agent
    #research_assistant_prompt = generate_research_assistant_prompt()

    # Retrieve long-term memory preferences if available
    memory = "None" 
    if "loaded_memory" in state: 
        memory = state["loaded_memory"]

    research_assistant_prompt = generate_research_assistant_prompt(memory = memory, prompt = state["messages"][0].content)
    print (f" Research Assistant Prompt ::::::::::: {research_assistant_prompt}")
    print (f" State Messages  ::::::::::: {state["messages"]}")

    messages_1 = [
        {"role": "system", "content": research_assistant_prompt},
    ] + state["messages"]

    # Invoke the language model with tools and system prompt
    # The model can decide whether to use tools or respond directly

    print(f"Invoking LLM noq...... {state["messages"]} and complete_message = {messages_1}")
    response = llm_model.invoke(messages_1)
    
    print(f"Message Response=====================  {response.content}")
    #print(f"Message Response=====================  {response.service_name}")
    #print(f"Message Response=====================  {response.action}")
    python_object = json.loads(response.content)

    print(f"Type of python_object: {type(python_object)}")
    print(f"Content of python_object: {python_object}")

    
    # Return updated state with the assistant's response
    return {"messages": [python_object]}

def should_continue(state: State, config: RunnableConfig):
    """
    Conditional edge function that determines the next step in the workflow.
    
    This function examines the last message in the conversation to decide whether the agent
    should continue with tool execution or end the conversation.
    
    Args:
        state (State): Current state containing messages and other workflow data
        config (RunnableConfig): Configuration for the runnable execution
        
    Returns:
        str: Either "continue" to execute tools or "end" to finish the workflow
    """
    
    print("Inside should contine")
    # Get all messages from the current state
    messages = state["messages"]

    print (f"messages  :::::::::::::::::::::: {messages}")

    # Examine the most recent message to check for tool calls
    last_message = messages[-1]
    
    print (f"Last message Tool calls :::::::::::::::::::::: {last_message.tool_calls}")
    # If the last message doesn't contain any tool calls, the agent is done
    if not last_message.tool_calls:
        return "end"
    # If there are tool calls present, continue to execute them
    else:
        return "continue"    

