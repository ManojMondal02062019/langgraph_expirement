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
        graph = builder.compile(checkpointer=memory)     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")
    
    #graph = builder.compile(checkpointer=memory)     

    #app_graph = graph.get_graph(xray=True) 
    #print_graph(app_graph)
    #app_graph.print_ascii()
    #app_graph.print_ascii()


    return graph

def human_node_working(state: AgentState):
    print(f"Node started with state: {state}")
    # Present current state to human and pause execution
    value = interrupt({
        "text_to_review": "Please review the service and corresponding actions. Use Approve, Edit, Modify keywords to provide your feedback"
    })
    print(f"Received human input: {value}")
    # When resumed, this will contain the human's input
    return {
        "final_output": value
    }

def human_node(state: AgentState) -> Command[Literal["commandexecute_agent", "identifyservice_agent"]]:
    print(f"Node started with state: {state}")
    # Present current state to human and pause execution
    value = interrupt({
        "text_to_review": "Please review the service and corresponding actions. Use Approve, Edit, Modify keywords to provide your feedback"
    })
    print(f"Received human input----------------------- {value}")
    # When resumed, this will contain the human's input
    if value == "approve":
        print(f"Received human input----------------------- Approve")
        return Command(goto="commandexecute_agent", update={"final_output": "approved"})
    elif value == "modify":
        print(f"Received human input----------------------- Modified")
        return Command(goto="identifyservice_agent", update={"final_output": "modify"})    
    else:
        print(f"Received human input----------------------- Rejected")
        return Command(goto=END, update={"final_output": "Thankyou. You can again start a new search"})
