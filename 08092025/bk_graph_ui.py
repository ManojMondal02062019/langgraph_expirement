import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import AgentState
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph
from langchain_core.messages import HumanMessage, AIMessage

def generate_uuid() -> str:
    return str(uuid.uuid4())

def run_chat():
    print("----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    try:
        if user_input := st.chat_input("You: "):
            print(f'Main: User Input : {user_input}')
            to_display = f"**User:** {user_input}"
            #  Display all previous messages
            print(f"State Messages : {st.session_state.messages}")
            for message in st.session_state.messages:
                st.markdown(message) 
            st.session_state.messages.append(to_display)
            st.markdown(to_display)
            thread_id = generate_uuid()
            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            } 
            #config: RunnableConfig = {"configurable": {"thread_id": thread_id}}           
            with st.spinner("Processing..."):   
                placeholder = st.container()  # Placeholder for dynamically updating agents message
                shared_state = {
                    "graph_resume": st.session_state.graph_resume
                }

                if user_input.lower() in ["exit", "quit", "bye"]:
                    save_checkpoint(thread_id, st.session_state.history)
                    st.markdown(f"\nConversation Saved. Resume using ID: {thread_id}")
                    st.markdown("---")
                elif user_input.lower().__contains__("old id"):
                    extract_id = user_input.split(":")
                    thread_id = extract_id[1].strip()
                    print(f"Retrieving conversation from thread id: {thread_id}")
                    old_messages = load_checkpoint(thread_id)
                    st.markdown(f"\nLoading old conversation using ID: {thread_id}")
                    human_messages = []
                    ai_messages = []
                    for message in old_messages["messages"]:
                        if isinstance(message, HumanMessage):
                            human_messages.append("User: " + message.content)
                        elif isinstance(message, AIMessage):
                            ai_messages.append(f"AI: " + message.content)
                    for num in range(len(human_messages)):
                        st.markdown(human_messages[num])
                        st.markdown(ai_messages[num])
                else:
                    state["messages"].append(HumanMessage(content=user_input))
                    placeholder = st.container()  # Placeholder for dynamically updating agents message
                    shared_state = {
                        "graph_resume": st.session_state.graph_resume
                    }

                    try:
                        #state = buildgraph().invoke(state, config)
                        for event in buildgraph().stream(state, config, stream_mode="values"):
                            print(f"Main EVENT :: {event}") 
                            print(f"Main :: State Message Content :: {event['messages'][-1].content}")
                            print(f"Main :: :::::::::::::::::::::::::: ")
                            content = event["messages"][-1].content
                            if "Please confirm the service and action" in content:
                                to_display = f"**Agent:** {event["messages"][-1].content}"
                                state["messages"].append(AIMessage(content=to_display))
                                st.session_state.messages.append(to_display)
                                st.markdown(to_display)
                                st.markdown("---")
                    except Exception as e:
                        st.markdown(f"Error during graph invocation: {e}")
                        st.markdown("---")
                        traceback.print_stack()
    except Exception as e:
        traceback.print_stack()
    st.session_state.history["messages"] = state["messages"]
    print("----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query") 

if 'graph_resume' not in st.session_state:
    st.session_state.graph_resume = False  # Track if the graph should resume from a previous state    

# Session state management for expander and graph resume after interrupt
if "expander_open" not in st.session_state:
    st.session_state.expander_open = True  # Initially keep expander open

if 'graph_resume' not in st.session_state:
    st.session_state.graph_resume = False  # Track if the graph should resume from a previous state


run_chat()