import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, approved_node
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot

def generate_uuid() -> str:
    return str(uuid.uuid4())

def run_chat(thread_id):
    print("----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    } 
    if user_input := st.chat_input("You: "):
        print(f'*** Main: User Input: {user_input}')
        to_display = f"**User:** {user_input}"
        st.session_state.messages.append(to_display)

        #display old messages
        for message in st.session_state.messages:
            st.markdown(message) 

        if user_input.lower() in ["exit", "quit", "bye"]:
            save_checkpoint(thread_id, st.session_state.history)
            st.markdown(f"\nConversation Saved. Resume using ID: {thread_id}. Bye until then")
            st.markdown("---")
            quit()

        print(f" Main :: Check graph State :: {buildgraph().get_state(config)}")
        state_snapshot = buildgraph().get_state(config)
        tool_output = state_snapshot.interrupts        
        print(f" Main :: Interrupt Tool Output :: {tool_output}")
        if (len(tool_output) > 0):
            if ("ok" in user_input.strip().lower()):
                approved_node(config)
            else:
                st.session_state.messages.append("Please enter OK, to proceed")
                st.markdown("Please enter OK, to proceed")
        else:
            with st.spinner("Processing..."):   
                if user_input.lower().__contains__("old id"):
                    extract_id = user_input.split(":")
                    thread_id = extract_id[1].strip()
                    old_messages = load_checkpoint(thread_id)
                    st.markdown(f"\nLoading old conversation using ID: {thread_id}")
                    st.session_state.messages.append(f"**Loading old conversation using ID: {thread_id}")
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
                    for event in buildgraph().stream(state, config, stream_mode="values"):
                        response = buildgraph().get_state(config)
                        final_output = response.values.get("final_output", "")
                        if len(final_output) > 0:
                            to_display = f"**Agent:** {final_output}"
                            state["messages"].append(AIMessage(content=to_display))
                            st.session_state.messages.append(to_display)
                            st.markdown(to_display)
                            st.markdown("---")
    print("----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")

run_chat(generate_uuid())