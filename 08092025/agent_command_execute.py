from agent_state import AgentState
from llm_model import llm, agent
from prompts import command_pre_service_prompt, command_join_validation_error_prompt
from langchain_core.messages import AIMessage
from utils import cleanJson
from langgraph.types import interrupt, Command

def commandexecute_agent(state: AgentState) -> AgentState:
    print(f"commandexecute: State Message: {state["messages"]}")
    user_msg = state["aws_service_attr"]
    response_text = "Sorry, I couldn't process your request."
    print(f"Command Execute :: User Message: {str(user_msg)}")
    prompt = command_pre_service_prompt.replace("##", str(user_msg))
    

    messages = [
        ("system", prompt),
        ("human", str(user_msg)),
    ]        
    response_text = llm.invoke(messages).content
    response_text = cleanJson(response_text)

    print(f"CommandExecute: Response : {response_text}")

    if (len(response_text) > 0):
        prompt = command_join_validation_error_prompt.replace("##", str(response_text))
        messages = [
            ("system", prompt),
            ("human", str(response_text)),
        ]        
        response_text = llm.invoke(messages).content
        print(f"CommandExecute: For validation/error, Response : {response_text}")

        if (len(response_text) > 0):
            print("INVOKED INTERRUPT - COMMAND EXECUTE")
            value = interrupt({
                "text_to_review": str(response_text),
                "final_output": str(response_text)
            })

            print(f"Received human input----------------------- {value}")
            #return Command(goto="commandexecute_agent", update={"final_output": "approved"})
            return Command(goto="commandexecute_agent")
        else:
            #all required parameters we have it
            # let's remove the pass and invoke python code to run the cli
            message = "Success. Let's execute it"
            current_messages = []  
            current_messages.append(AIMessage(content=message))
            return {
                "messages": message,
                "final_output": message,
            }
        