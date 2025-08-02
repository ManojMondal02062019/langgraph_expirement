from langgraph.graph import StateGraph, END
from sharedstate import GraphState
from general_chat import chat_agent
from identifyservice import identifyservice_agent
from router_agent import route

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
    builder = StateGraph(GraphState)
    builder.add_node("chat_agent", chat_agent)
    builder.add_node("identifyservice_agent", identifyservice_agent)
    builder.add_node("route", lambda x: x)

    builder.add_conditional_edges("route", route, {
        "chat_agent": "chat_agent",
        "identifyservice_agent": "identifyservice_agent"
    })

    builder.set_entry_point("route")
    builder.add_edge("chat_agent", END)
    builder.add_edge("identifyservice_agent", END)

    try:
        graph = builder.compile()     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")
    print(f'graphbuild: Returning graph builder')
    return graph