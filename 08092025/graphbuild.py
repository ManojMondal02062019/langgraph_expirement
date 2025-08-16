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

def resume_graph(config: RunnableConfig):
    final_result = buildgraph().invoke(Command(resume="approve"), config=config)
    print("Resume Graph")  

def reject_graph(config: RunnableConfig):
    final_result = buildgraph().invoke(None, config=config)
    print("Start again")  

def modify_graph(config: RunnableConfig):
    final_result = buildgraph().invoke(Command(resume="modify"), config=config)
    print("Start again")  

def clear_update_graph_state(config):
    # Get the checkpointed state
    checkpoint = buildgraph().get_state(config)
    modified_state = checkpoint.values
    modified_state["final_output"] = ""
    buildgraph().update_state(config, modified_state)
    print(f"****** clear_update_graph_state Completed")

# Next steps after approval
def approved_node(thread_config: str):
    print("Approved path taken.")
    buildgraph().invoke(Command(resume="ok"), thread_config)

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
    #tools = [validate_params]
    #model_with_tools = llm().bind_tools(tools, parallel_tool_calls=False)
    builder = StateGraph(AgentState)
    builder.add_node("chat_agent", chat_agent)
    builder.add_node("intent_agent", intent_agent)
    builder.add_node("identifyservice_agent", identifyservice_agent)
    builder.add_node("commandexecute_agent", commandexecute_agent)
    builder.add_node("human_approval", human_approval)
    #builder.add_node("approved_intent_path", approved_node)
    #builder.add_node("rejected_intent_path", rejected_node)
    #builder.add_node("modify_intent_path", modify_node)
    builder.add_node("route", lambda x: x)
    
    # commented on 08162025
    builder.add_conditional_edges("route", route, {
        "chat_agent": "chat_agent",
        "intent_agent": "intent_agent"
    })

    #builder.add_conditional_edges(
    #    "decider",
    #    lambda s: s["query"],         # returns "search" or "direct"
    #    {"search": "search", "direct": "answer"}
    #)
    builder.set_entry_point("route")
    builder.add_edge("chat_agent", END)
    builder.add_edge("intent_agent", "identifyservice_agent")
    builder.add_edge("identifyservice_agent", "human_approval")
    builder.add_edge("human_approval", "commandexecute_agent")
    builder.add_edge("human_approval", "identifyservice_agent")
    builder.add_edge("commandexecute_agent", END)

    try:
        graph = builder.compile(checkpointer=memory)     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")

    #app_graph = graph.get_graph(xray=True) 
    #print_graph(app_graph)
    #app_graph.print_ascii()


    return graph

'''

    app_graph = graph.get_graph(xray=True) 
    print_graph(app_graph)
    app_graph.print_ascii()
    #print("Graph Printed")
'''

# Human approval node
def human_approval(state: AgentState, config: RunnableConfig) -> Command[Literal["commandexecute_agent", "identifyservice_agent"]]:

    # Generate the human approval message
    approval_message = f"Kindly confirm to proceed OR you can modify your query (A=Approve, R=Reject and begin from start, M=Modify the intent?"

    # Pause the graph and surface the approval message
    decision = interrupt({"message": approval_message})    
    #decision = interrupt({
    #    "question": "Do you approve, reject the following output? OR you want to modify the request",
    #    "llm_output": state["llm_output"]
    #})

    if decision == "approve" or decision == "A":
        print(f" DECISION APPROVED .... {decision}")
        return Command(goto="commandexecute_agent", update={"decision": "approved"})
    elif decision == "reject" or decision == "R":
        print(f" DECISION REJECTED .... {decision}")
        pass
    else:
        print(f" DECISION MODIFY .... {decision}")
        return Command(goto="identifyservice_agent", update={"decision": "modify"})

# Human approval node
def human_approval1(state: AgentState, config: RunnableConfig) -> Command[Literal["commandexecute_agent", "identifyservice_agent"]]:

    # Generate the human approval message
    approval_message = f"Kindly confirm to proceed OR you can modify your query ?"

    # Pause the graph and surface the approval message
    decision = interrupt({"message": approval_message})    
    #decision = interrupt({
    #    "question": "Do you approve, reject the following output? OR you want to modify the request",
    #    "llm_output": state["llm_output"]
    #})

    if decision == "approve":
        print(f" DECISION APPROVED .... {decision}")
        return Command(goto="commandexecute_agent")
    elif decision == "reject":
        print(f" DECISION REJECTED .... {decision}")
        return Command(goto="rejected_intent_path", update={"decision": "rejected"})
    else:
        print(f" DECISION MODIFY .... {decision}")
        return Command(goto="modify_intent_path", update={"decision": "modify"})

# Next steps after approval
def approved_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Approved path taken......11111")
    return state

# Alternative path after rejection
def rejected_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Rejected path taken...22222")
    return state

# Alternative path after rejection
def modify_node(state: AgentState, config: RunnableConfig) -> AgentState:
    print("Rejected path taken.....33333")
    return state
