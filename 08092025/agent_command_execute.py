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
        if isinstance(msg, HumanMessage) and msg not in human_messages:
            human_messages.append(msg.content)
    
    print(f"Get the prompt -> {summary_prompt}")

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

    print(f"CommandExecute: Check parameters (on missing field, if any): {response_text}")

    # if there are error messages or validation messages, then we need to interrupt to get user input
    response_text, aws_keys, aws_values = parseJSONForErrorMessages(response_text)
    print(f"Commandexecute: Error Messages if any (after parse): {response_text}")

    if len(response_text) > 0:
        response_messages = []
        final_response = "Values for the below parameters required to proceed: \n\n"
        tmp_response = ""
        slno = 1
        for response in response_text:
            tmp_response = tmp_response + f"({slno}) {response}, "
            print(f">> {slno}. CommandExecute: Iterate {tmp_response}")
            slno = slno + 1
        
        response_messages.append(AIMessage(content=str(final_response + tmp_response)))
        state["messages"] = response_messages
        state["approval_status"] = "notapproved"
    else:
        # response is good to proceed with.
        print("CommandExecute: Approved")
        aws_service_values = {key: value for key, value in zip(aws_keys, aws_values)}
        response_messages = []
        response_messages.append(AIMessage(content=str(aws_service_values)))
        state["messages"] = response_messages
        state["aws_service_values"] = aws_service_values
        state["approval_status"] = "approve"
    
    return state

def pre_commandexecute_agent(state: AgentState) -> AgentState:
    print(f"PreCommandExecute, state: {state}")
    if state["approval_status"] == "approve":
        print("PreCommandExecute, Go to next step")
    else:
        response_text = state["messages"][-1].content
        print(f"pre_commandexecute_agent: response : {response_text}")
        value = interrupt({
            "text_to_review": response_text
        })
        print(f"PreCommandExecute, User Response received: {value}")
        human_message = []
        human_message.append(HumanMessage(content=value))
        state["messages"] = human_message
        state["approval_status"] = "notapproved"
    return state
