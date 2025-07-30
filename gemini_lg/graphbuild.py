from langgraph.graph import StateGraph, END
from sharedstate import GraphState
from general_chat import chat_agent
from identifyservice import identifyservice_agent

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