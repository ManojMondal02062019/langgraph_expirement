from agent_state import AgentState
from llm_model import llm, agent
from prompts import command_pre_service_prompt, command_join_validation_error_prompt, summary_prompt
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command


def commandexecute_agent(state: AgentState) -> AgentState:
    print(f"Commandexecute: State Message: {state["messages"]}")
    user_msg = state["aws_service_attr"]
    response_text = "Sorry, I couldn't process your request."

    human_messages = []

    # to find all the required parameters
    prompt = command_pre_service_prompt.replace("#params#", str(user_msg))

    # read all the human messages as values will be in human messages only
    #summarized message
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            human_messages.append("User: " + msg.content)
    
    # now we have to summarize the user input
    messages = [
        ("system", summary_prompt),
        ("human", str(human_messages)),
    ]        
    response_text = llm.invoke(messages).content
    print(f"Commandexecute: Summarized Message: {response_text}")

    # add the summarized message as an input to llm
    prompt = command_pre_service_prompt.replace("#human#", str(response_text))
    
    messages = [
        ("system", prompt),
        ("human", str(user_msg)),
    ]
    response_text = llm.invoke(messages).content
    response_text = cleanJson(response_text)

    print(f"CommandExecute: Response to check parameters (on missing field): {response_text}")

    # if there are error messages or validation messages, then we need to interrupt to get user input
    response_text = parseJSONForErrorMessages(response_text)
    print(f"Commandexecute: Error Messages if any :: {response_text}")
    if len(response_text) > 0:
        value = interrupt({
            "text_to_review": f"Error found. Please correct the following messages: {response_text}"
        })
    else:
        response_messages = []
        response_messages.append(AIMessage(content=str(response_text)))
        return {
            "messages": response_messages,
            "final_output": str(response_text)
        }

    # below code will be executed, if interrupted
    print(f"CommandExecute: Received Human Input: {value}")
    
    # When resumed, this will contain the human's input
    if len(value.lower()) > 0:
        state["messages"].append(HumanMessage(content=value))
        return Command(goto="commandexecute_agent")
    else:
        return Command(goto=END, update={"final_output": "You are good for execution"})