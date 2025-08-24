from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_chat import chat_agent
from agent_identify_service import identifyservice_agent
from agent_command_execute import commandexecute_agent
from agent_intent import intent_agent
from router_agent import route
from llm_model import llm, memory
from typing import Literal
from langgraph.types import interrupt, Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.utils import filter_messages

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

def buildgraph():
    # Define tools and bind them to model
    builder = StateGraph(AgentState)
    builder.add_node("chat_agent", chat_agent)
    builder.add_node("intent_agent", intent_agent)
    builder.add_node("identifyservice_agent", identifyservice_agent)
    builder.add_node("commandexecute_agent", commandexecute_agent)
    builder.add_node("human_review_node", human_node)
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
    #builder.add_edge("commandexecute_agent", "review_pre_condition")
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
    #print_graph(app_graph)
    #app_graph.print_ascii()

    return graph

def human_node(state: AgentState) -> Command[Literal["commandexecute_agent", "identifyservice_agent"]]:
    print(f"GraphBuild: human_node, State : {state}")
    question_msg = "Please review the service and corresponding actions. Use Approve, Edit, Modify keywords to provide your feedback"
    # set the interrupt message as well
    updateStateWithAIMessage(None, question_msg, state)
    print(f"GraphBuild: human_node, Invoke Interrupt and also state is updated, State : {state}")
    # Present current state to human and pause execution
    value = interrupt({
        "text_to_review": question_msg
    })

    # When resumed, this will contain the human's input
    print(f"GraphBuild: human_node - {value}")
    
    if value.lower() == "approve":
        state["interrupt_flag"] = False
        return Command(goto="commandexecute_agent")
    elif value.lower() == "modify":
        state["interrupt_flag"] = False
        return Command(goto="identifyservice_agent")    
    elif value.lower() == "rejected":
        state["interrupt_flag"] = False
        return Command(goto=END, update={"final_output": "Thankyou. You can again start a new search"})
    else:
        state["interrupt_flag"] = True
        pass
        

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
        #return Command(goto="commandexecute_agent", update={"final_output": "approved"})
        state["interrupt_flag"] = False
        return Command(goto="commandexecute_agent")
    elif value.lower() == "modify":
        state["interrupt_flag"] = False
        return Command(goto="identifyservice_agent")    
    elif value.lower() == "rejected":
        state["interrupt_flag"] = False
        new_ai_message = AIMessage(content="Thankyou. You can again start a new search")
        return Command(goto=END, update={"messages": state.messages + [new_ai_message]})
    else:
        state["interrupt_flag"] = True
        pass

def chkHumanLoop(config, user_input):
    # check for interrupts any
    chkInterruptMessage, next_state = checkInterrupts(config)
    print(f"GraphBuild : chkHumanLoop: chkInterruptMessage : {chkInterruptMessage}")
    approved_values = ["approve","modify","rejected"]
    #final_result = ""

    print(f"Graphbuild: chkHumanLoop:: user_input: {user_input}")

    if (len(chkInterruptMessage) > 0):
        if ("human_review_node" in next_state):
            found = [item for item in approved_values if item == user_input.lower()]
            if found:
                buildgraph().invoke(Command(resume=user_input), config=config)                
        elif ("commandexecute_agent" in next_state):
            buildgraph().invoke(Command(resume=user_input), config=config)

        return stateMessagesAndInterrupt(config,True)
    else:
        print("Graphbuild: chkHumanLoop:: No Interruption")
        return None
    

def checkInterrupts(config):
    state_snapshot = buildgraph().get_state(config)
    print (f"Graphbuild: checkInterrupts state_snapshot ::::::::::::::: {state_snapshot}")
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
    print(f"Graphbuild: checkInterruptFlag: {state_snapshot.values.get("interrupt_flag")}")
    return state_snapshot.values.get("interrupt_flag")

def updateStateWithAIMessage(config, ai_new_message, state:AgentState):
    if config is not None:
        new_message = AIMessage(content=ai_new_message)
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
        messages.append(readInterruptMessages(state_snapshot))
    else:
        int_msg = readInterruptMessages(state_snapshot)
        if (len(int_msg) > 0):
            messages.append(int_msg)
        else:
            messages.append(readAIMessages(state_snapshot))
    return messages