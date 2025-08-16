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
from utils import human_approval, approved_node, rejected_node, modify_node
from langchain_core.runnables import RunnableConfig

def resume_graph(config: RunnableConfig):
    final_result = buildgraph().invoke(Command(resume="approve"), config=config)
    print(final_result)  

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
    builder.add_node("approved_intent_path", approved_node)
    builder.add_node("rejected_intent_path", rejected_node)
    builder.add_node("modify_intent_path", modify_node)
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
    builder.add_edge("approved_intent_path", "commandexecute_agent")
    builder.add_edge("rejected_intent_path", "identifyservice_agent")
    builder.add_edge("modify_intent_path", "identifyservice_agent")
    builder.add_edge("commandexecute_agent", END)

    try:
        graph = builder.compile(checkpointer=memory)     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")

    return graph

'''

    app_graph = graph.get_graph(xray=True) 
    print_graph(app_graph)
    app_graph.print_ascii()
    #print("Graph Printed")

def buildgraphv2(state, config, prompt, placeholder, shared_state):

    container = st_placeholder 
    st_input = {"input": st_messages} # user enter a statement

    if st_state.get("graph_resume"):

        graph.update_state(thread_config, {"input": st_messages})  # Update the graph's state with the new input
        st_input = None  # No new input is passed if resuming the graph

    async for event in graph.astream_events(st_input, thread_config, version="v2"):
        name = event["name"]

        if name == "on_conditional_check":
            container.info("The length of the word is " + str(event["data"]) + " letters long")

        # the graph issued an interrupt that the user needs to update/handle
        if name == "on_waiting_user_resp":
            # Display the issue/error and prompt the user for a new response or update
            container.error("The length of the word is " + str(event["data"]) + " letters long")

        if name == "on_complete_graph":
            with container:
                st.balloons()
                data = event["data"]
            # Return success message with processed data
            return {"op": "on_new_graph_msg", "msg": f"Nice, the word is {data['input']}, with length {data['len']}"}

    state = graph.get_state(thread_config)

    # If there are any pending tasks and interruptions, handle them
    if len(state.tasks) != 0 and len(state.next) != 0:
        issue = state.tasks[0].interrupts[0].value  # Retrieve the first interrupt value from the task
        # Return an operation indicating the graph is waiting for the user to respond
        return {"op": "on_waiting_user_resp", "msg": issue}
'''