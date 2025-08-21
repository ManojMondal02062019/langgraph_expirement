from agent_state import AgentState
from llm_model import llm, agent
from prompts import command_pre_service_prompt, command_join_validation_error_prompt, summary_prompt
from langchain_core.messages import AIMessage, HumanMessage
from utils import cleanJson, parseJSONForErrorMessages
from langgraph.types import interrupt, Command


def commandexecute_agent(state: AgentState) -> AgentState:
    print(f"commandexecute: State Message: {state["messages"]}")
    user_msg = state["aws_service_attr"]
    response_text = "Sorry, I couldn't process your request."
    # to find all the required parameters
    prompt = command_pre_service_prompt.replace("#params#", str(user_msg))
    human_messages = []
    # read all the human messages as values will be in human messages only
    #summarized message
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            human_messages.append("User: " + msg.content)
            messages = [
                ("system", summary_prompt),
                ("human", str(human_messages)),
            ]        
            response_text = llm.invoke(messages).content
            print(f"Summarized Message: {response_text}")

    prompt = command_pre_service_prompt.replace("#human#", str(response_text))
    
    messages = [
        ("system", prompt),
        ("human", str(user_msg)),
    ]        
    response_text = llm.invoke(messages).content
    response_text = cleanJson(response_text)

    print(f"CommandExecute: JSON Response (on missing field): {response_text}")

    current_messages = []  
    current_messages.append(AIMessage(content=response_text))

    # if there are error messages or validation messages, then we need to interrupt to get user input
    error_messages_if_any = parseJSONForErrorMessages(response_text)
    print(f" Error Messages if any :: {error_messages_if_any}")
    if len(error_messages_if_any) > 0:
        value = interrupt({
            "text_to_review": f"Please correct the following messages: {error_messages_if_any}"
        })

    print(f"Command Execute: Received human input----------------------- {value}")
    
    # When resumed, this will contain the human's input
    if len(value.lower()) > 0:
        print(f"Command Execute: Received human input----------------------- Approve")
        state["messages"].append(HumanMessage(content=value))
        return Command(goto="commandexecute_agent")
    else:
        print(f"Received human input----------------------- Rejected")
        return Command(goto=END, update={"final_output": "You are good for execution"})


def review_pre_condition_agent(state: AgentState) -> AgentState:
    print("CommandAgent :: review_pre_condition_agent....")
    response_text = "Inside review Pre Condition Agent"
    return {
        "messages": response_text,
        "approved": False
    }

def procced_with_execution_agent(state: AgentState) -> AgentState:
    print("CommandAgent :: proceed_with_execution_agent....")
    pass
