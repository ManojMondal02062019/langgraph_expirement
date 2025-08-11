from langgraph.graph import StateGraph, END
from agent_state import AgentState
from agent_chat import chat_agent
from agent_identify_service import identifyservice_agent
from agent_command_execute import commandexecute_agent
from agent_intent import intent_agent
from router_agent import route
from llm_model import llm, checkpointer
from typing import Literal
from langgraph.types import interrupt, Command

'''
# Simulate an LLM output node
def generate_llm_output(state: AgentState) -> AgentState:
    return {"llm_output": "This is the generated output."}

def human_approval(state: AgentState) -> Command[Literal["approved_path", "rejected_path"]]:
    decision = interrupt({
        "question": "Do you approve the following output?",
        "llm_output": state["llm_output"]
    })

    if decision == "approve":
        return Command(goto="approved_path", update={"decision": "approved"})
    else:
        return Command(goto="rejected_path", update={"decision": "rejected"})

# Next steps after approval
def approved_node(state: AgentState) -> AgentState:
    print("Approved path taken.")
    return state

# Alternative path after rejection
def rejected_node(state: AgentState) -> AgentState:
    print("Rejected path taken.")
    return state
'''

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
    builder.add_node("route", lambda x: x)
    
    builder.add_conditional_edges("route", route, {
        "chat_agent": "chat_agent",
        "intent_agent": "intent_agent"
    })

    #builder.add_conditional_edges("tool", should_continue, {
    #    "continue": "agent",
    #    "end": END,
    #    "call_tool": "tool"
    #})

    builder.set_entry_point("route")
    builder.add_edge("chat_agent", END)
    builder.add_edge("intent_agent", "identifyservice_agent")
    builder.add_edge("identifyservice_agent", END)
    #builder.add_edge("identifyservice_agent", "commandexecute_agent")
    #builder.add_edge("commandexecute_agent", END)

    try:
        graph = builder.compile(checkpointer=checkpointer)     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")

    #app_graph = graph.get_graph(xray=True) 
    #print_graph(app_graph)
    #app_graph.print_ascii()
    #print("Graph Printed")
    return graph

'''
def buildgraphv2(st_messages, st_placeholder, st_state):

    container = st_placeholder
    st_input = {"input": st_messages}

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