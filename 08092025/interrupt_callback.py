from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.config import RunnableConfig
#  https://api.python.langchain.com/en/latest/callbacks/langchain_core.callbacks.manager.adispatch_custom_event.html
from langchain_core.callbacks import adispatch_custom_event
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt

async def step_1(state, config: RunnableConfig):
    print("---Step 1---")
    # Dispatch a custom event to notify about the initialization of the input
    # currently we don't do anything with this, but flexibility is there
    await adispatch_custom_event("on_init_input", {"input": state["input"]}, config=config)
    print("---Step 11---")
    return state

async def step_2(state, config: RunnableConfig):
    print("---Step 2---")
    if len(state['input']) > 5:
        # Dispatch an event indicating the need for user response (input is too long)
        await adispatch_custom_event("on_waiting_user_resp", len(state["input"]), config=config)
        # Raise a NodeInterrupt to stop execution and request a shorter input (<= 5 characters)
        print("---Step 21---")
        raise NodeInterrupt(f"Please provide an input </= than 5 characters, current is {state['input']}, with length {len(state['input'])}")
    else:
        # Dispatch an event confirming that the input meets the length condition
        print("---Step 22---")
        await adispatch_custom_event("on_conditional_check", len(state["input"]), config=config)

async def step_3(state, config: RunnableConfig):
    print("---Step 3---")
    # Dispatch an event indicating the graph has completed with the given input and its length
    await adispatch_custom_event("on_complete_graph", {"input": state["input"], "len": len(state["input"])}, config=config)
    print("---Step 31---")
    return state
