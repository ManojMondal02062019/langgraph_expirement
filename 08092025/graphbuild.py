from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_chat import chat_agent
from agent_identify_service import identifyservice_agent
from agent_command_execute import commandexecute_agent, pre_commandexecute_agent
from agent_run_command import runcommand_agent
from agent_intent import intent_agent
from router_agent import route
from llm_model import llm, memory
from typing import Literal
from langgraph.types import interrupt, Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import filter_messages
from langgraph.prebuilt import ToolNode
from agent_run_command import runcommand_agent

#from langchain_core.runnables.human_input import HumanInput

def print_graph(graph):
        
    # Assuming graph has methods or attributes to access nodes and edges
    nodes = graph.nodes  # Adjust according to actual method/attribute to access nodes
    edges = graph.edges  # Adjust according to actual method/attribute to access edges

    print("Nodes:")
    for node in nodes:
        print(f"  {node}")

    print("\nEdges:")
    for edge in edges:
        print(f"  {edge[0]} -> {edge[1]}")

# Define the routing logic (should_continue)
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END # If no tool call, end the graph

def buildgraph():

    # Node to handle tool invocation
    #tool_node = ToolNode([executeAWSCommandTool])

    # Define tools and bind them to model
    builder = StateGraph(AgentState)
    builder.add_node("chat_agent", chat_agent)
    builder.add_node("intent_agent", intent_agent)
    builder.add_node("identifyservice_agent", identifyservice_agent)
    builder.add_node("commandexecute_agent", commandexecute_agent)
    #builder.add_node("agent_run_command",runcommand_agent)
    #builder.add_node("tool_invocation_node", tool_node)
    builder.add_node("human_review_node", human_node)
    builder.add_node("pre_commandexecute_agent",pre_commandexecute_agent)
    builder.add_node("agent_run_command",runcommand_agent)
    #builder.add_node("review_pre_condition", review_pre_condition_agent)
    #builder.add_node("proccedwithexecution", procced_with_execution_agent)
    #builder.add_node("human_ask_parameter", human_ask_node)
    builder.add_node("route", lambda x: x)

    
    builder.set_entry_point("route")
    # commented on 08162025
    builder.add_conditional_edges("route", route, {
        "chat_agent": "chat_agent",
        "intent_agent": "intent_agent"
    })

    builder.add_edge("chat_agent", END)
    builder.add_edge("intent_agent", "identifyservice_agent")
    builder.add_edge("identifyservice_agent", "human_review_node")
    #builder.add_edge("human_review_node","commandexecute_agent")
    builder.add_edge("commandexecute_agent","pre_commandexecute_agent")
    # Define conditional edge based on approval status
    builder.add_conditional_edges(
        source="pre_commandexecute_agent",
        path=lambda state: "commandexecute_agent" if state["approval_status"] != "approve" else "agent_run_command",
    )
    #builder.add_conditional_edges(
    #    "pre_commandexecute_agent",
    #    lambda state: state["approval_status"],{
    #        "commandexecute_agent": "approve",
    #        "pre_commandexecute_agent" : "notapproved"
    #    })
    builder.add_edge("agent_run_command", END)
    #builder.add_conditional_edges(
    #    "agent_run_command",
    #    should_continue,
    #    {"tools": "tool_invocation_node", END: END}
    #)    
    
    #builder.add_conditional_edges(
    #    "review_pre_condition",
    #    lambda state: "proccedwithexecution" if state["approved"] else "commandexecute_agent"
    #)
    #builder.add_edge("proccedwithexecution", END)
    # Conditional routing based on human review
    #builder.add_conditional_edges(
    #    "human_review_node",
    #    human_approval,
    #    {
    #        "approved": "commandexecute_agent",
    #        "modify": "identifyservice_agent", # Loop back for invalid input
    #    }
    #)
    #builder.add_edge("commandexecute_agent", END)

    try:

        #graph = builder.compile(checkpointer=memory, interrupt_after=["commandexecute_agent"])     
        graph = builder.compile(checkpointer=memory)     

    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")
    
    #app_graph = graph.get_graph(xray=True) 
    #app_graph.print_ascii()

    return graph

#check this tutorial for accepting correct user_input
# https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/#validate-human-input
def human_node(state: AgentState) -> Command[Literal["commandexecute_agent", "identifyservice_agent", END]]:
    print(f"GraphBuild: human_node, State : {state}")
    question_msg = "Please review the result and corresponding actions.\n\nUse OK or 1 (to continue), Edit or 2 (modify query), Exit or 3 (begin new) to proceed."
    user_msg = state["messages"][-1].content
    user_msg = f"{user_msg}\n\n{question_msg}"
    value = interrupt({
        "text_to_review": user_msg
    })
    # When resumed, this will contain the human's input
    print(f"GraphBuild: human_node, value is ------ {value}")
    new_ai_message = state["messages"]
    aws_service_attr = state["aws_service_attr"]
    if value.lower() == "ok" or value.lower() == "1":
        new_ai_message.append(AIMessage(content="Processing the request..."))
        goto="commandexecute_agent"
    elif value.lower() == "edit" or value.lower() == "2":
        new_ai_message.append(AIMessage(content="Modify your query..."))
        aws_service_attr = None
        goto="END"
    elif value.lower() == "exit" or value.lower() == "3":
        new_ai_message.append(AIMessage(content="Thankyou. You can again start a new search.."))        
        goto="END"
        aws_service_attr = None
    else:
        # do nothing and 
        print("NOTHING BLOCK")
        pass

    return Command(
        # this is the state update
        update={"messages": new_ai_message, "aws_service_attr": aws_service_attr},
        # this is a replacement for an edge
        goto=goto,
    )
        

def reviser_node(state: AgentState) -> AgentState:
    # ... logic to revise code based on feedback ...
    state.updated_code = state.original_code.replace("World", "LangGraph") # Example revision
    state.total_iterations += 1
    return state

def human_ask_node(state: AgentState) -> Command[Literal["commandexecute_agent"]]:
    print(f"GraphBuild: Human Ask Node, state: {state}")
    # Present current state to human and pause execution
    value = interrupt({
        "text_to_review": "Please review the service and corresponding actions. Use Approve, Edit, Modify keywords to provide your feedback"
    })
    print(f"GraphBuild: Received human input: {value}")
    # When resumed, this will contain the human's input
    if value.lower() == "approve":
        return Command(goto="commandexecute_agent")
    elif value.lower() == "modify":
        return Command(goto="identifyservice_agent")    
    elif value.lower() == "rejected":
        return Command(goto=END)
    else:
        pass

def chkHumanLoop(config, user_input):
    # check for interrupts any
    chkInterruptMessage, next_state = checkInterrupts(config)
    print(f"GraphBuild : chkHumanLoop: chkInterruptMessage : {chkInterruptMessage}")
    approved_values = ["approve","modify","start new"]
    #final_result = ""

    print(f"Graphbuild: chkHumanLoop:: user_input: {user_input}")

    if (chkInterruptMessage is not None and len(chkInterruptMessage) > 0):
        if ("human_review_node" in next_state):
            found = [item for item in approved_values if item == user_input.lower()]
            if found:
                buildgraph().invoke(Command(resume=user_input), config=config)                
        elif ("commandexecute_agent" in next_state):
            #buildgraph().invoke(Command(resume=user_input), config=config)
            print("NOTHIN TO EXECUTE AS COMMANDEXECUTE is handled by builder")

        return stateMessagesAndInterrupt(config,True)
    else:
        print("Graphbuild: chkHumanLoop:: No Interruption")
        return None
    

def checkInterrupts(config):
    state_snapshot = buildgraph().get_state(config)
    tool_output = state_snapshot.interrupts        
    if len(tool_output) > 0:
        return (tool_output[0].value).get("text_to_review"), state_snapshot.next
    else:
        return "",""

def human_node_working_1(state: AgentState):
    print(f"GraphBuild: Node started with state: {state}")
    # Present current state to human and pause execution
    value = interrupt({
        "text_to_review": "Please review the service and corresponding actions. Use Approve, Edit, Modify keywords to provide your feedback"
    })
    print(f"GraphBuild: Received human input: {value}")
    # When resumed, this will contain the human's input
    return {
        "final_output": value
    }

def checkInterruptFlag(config):
    state_snapshot = buildgraph().get_state(config)
    print(f"Graphbuild: checkInterruptFlag: {state_snapshot.interrupts}")
    return len(state_snapshot.interrupts) > 0

def updateStateWithAIMessage(config, ai_new_message, state:AgentState):
    if config is not None:
        new_message = AIMessage(content=ai_new_message)
        buildgraph().update_state(config, {"messages": [new_message]})
    else:
        state["messages"].append(AIMessage(content=str(ai_new_message)))

def updateStateWithHumanMessage(config, ai_new_message, state:AgentState):
    if config is not None:
        new_message = HumanMessage(content=ai_new_message)
        buildgraph().update_state(config, {"messages": [new_message]})
    else:
        state["messages"].append(AIMessage(content=str(ai_new_message)))

def stateWithAllMessage(config):
    state_snapshot = buildgraph().get_state(config)
    existing_message = state_snapshot.values.get("messages")
    print(f"GraphBuild : stateWithAllMessage : ALLLL MESSAGES ---------------- {existing_message}")
    return existing_message

def readAIMessages(state_snapshot):
    ai_messages = filter_messages(state_snapshot.values.get("messages"), include_types=["ai"])
    last_response = ""
    if (len(ai_messages) > 0):
        last_response = (ai_messages[len(ai_messages)-1]).content   
    return last_response

def readInterruptMessages(state_snapshot):
    interrupt_output = state_snapshot.interrupts
    last_response = ""
    if len(interrupt_output) > 0:
        last_response = (interrupt_output[0].value).get("text_to_review")
    return last_response


def stateMessagesAndInterrupt(config, interrupt_flow):
    messages=[]
    state_snapshot = buildgraph().get_state(config)
    if (not interrupt_flow):
        messages.append(readAIMessages(state_snapshot))
        #messages.append(readInterruptMessages(state_snapshot))
    else:
        int_msg = readInterruptMessages(state_snapshot)
        if (int_msg is not None and len(int_msg) > 0):
            messages.append(int_msg)
        else:
            messages.append(readAIMessages(state_snapshot))
    print(f"FF Graphbuild: stateMessagesAndInterrupt: {messages}")
    return messages

def readInterruptMessage(config):
    messages=[]
    state_snapshot = buildgraph().get_state(config)
    int_msg = readInterruptMessages(state_snapshot)
    if (int_msg is not None and len(int_msg) > 0):
        messages.append(int_msg)
    return messages    

def readInterruptMessageFromConfig(config):
    messages=[]
    state_snapshot = buildgraph().get_state(config)
    int_msg = readInterruptMessages(state_snapshot)
    if (int_msg is not None and len(int_msg) > 0):
        messages.append(int_msg)
    return messages    

def readAIMessagesFromConfig(config):
    state_snapshot = buildgraph().get_state(config)
    ai_messages = filter_messages(state_snapshot.values.get("messages"), include_types=["ai"])
    last_response = []
    if (len(ai_messages) > 0):
        last_response.append((ai_messages[len(ai_messages)-1]).content)
    return last_response

# Node to trim messages
def trim_messages_node(state: AgentState):
    messages = state["messages"]
    # Keep only the last 3 messages
    if len(messages) > 3:
        print(f"Trimmed State Messages")
        return {"messages": messages[-3:]}
    return {}