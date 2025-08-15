import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, approved_node, clear_update_graph_state
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot

thread_id = None

def generate_uuid() -> str:
    return str(uuid.uuid4())

def checkInterrupts(config):
    state_snapshot = buildgraph().get_state(config)
    tool_output = state_snapshot.interrupts        
    if len(tool_output) > 0:
        return (tool_output[0].value).get("message")
    else:
        return ""

def run_chat(thread_id):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    if user_input := st.chat_input("You: "):
        print(f'*** Main: User Input: {user_input}')
        to_display = f"**User:** {user_input}"
        st.session_state.messages.append(to_display)
        if thread_id == None:
            st.session_state.thread_id = generate_uuid()
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        } 

        #display old messages
        for message in st.session_state.messages:
            st.markdown(message) 

        if user_input.lower() in ["exit", "quit", "bye"]:
            save_checkpoint(thread_id, st.session_state.history)
            st.markdown(f"\nConversation Saved. Resume using ID: {thread_id}. Bye until then")
            st.markdown("---")
            quit()

        chkInterruptMessage=checkInterrupts(config)
        if (len(chkInterruptMessage) > 0):
            if ("ok" in user_input.strip().lower()):
                print("OK. From user")
                approved_node(config)
            else:
                print("Not OK. From user")
                st.markdown(chkInterruptMessage)
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
                        print(f" RESPONSE -> {response}")
                        final_output = response.values.get("final_output", "")
                        if len(final_output) > 0:
                            to_display = f"**Agent:** {final_output}"
                            state["messages"].append(AIMessage(content=to_display))
                            st.session_state.messages.append(to_display)
                            st.markdown(to_display)
                    clear_update_graph_state(config)
                    chkInterruptMessage = checkInterrupts(config)
                    if (len(chkInterruptMessage) > 0):
                        to_display = "\n" + chkInterruptMessage
                        st.markdown(to_display)
    print("----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.session_state.thread_id = generate_uuid()
    print(f"THREAD_ID : {st.session_state.thread_id}")
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")


run_chat(st.session_state.thread_id)