import streamlit as st
import uuid
from graphbuild import buildgraph
from langchain_core.messages import HumanMessage, AIMessage
from save_history import load_checkpoint, save_checkpoint
from sharedstate import GraphState

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
            for message in st.session_state.messages:
                st.markdown(message) 
            st.session_state.messages.append(to_display)
            st.markdown(to_display)
            thread_id = generate_uuid()
            with st.spinner("Processing..."):   
                if user_input.lower() in ["exit", "quit", "bye"]:
                    save_checkpoint(thread_id, st.session_state.history)
                    st.markdown(f"\nConversation Saved. Resume using ID: {thread_id}")
                    st.markdown("---")
                elif user_input.lower().__contains__("old id"):
                    print("Old Id block")
                    id = user_input.split(":")
                    for i in id:
                        thread_id = i
                    print(f"Thread Id 1111 :: {thread_id}")
                    old_messages = load_checkpoint(thread_id)
                    st.markdown(f"\nLoading old conversation using ID: {thread_id}")
                    human_messages = []
                    ai_messages = []
                    print(f"For Loop")
                    for message in old_messages["messages"]:
                        print(f"Inside For Loop")
                        if isinstance(message, HumanMessage):
                            print(f"For Loop, human message")
                            human_messages.append(message.content)
                        elif isinstance(message, AIMessage):
                            print(f"For Loop, aI message")
                            ai_messages.append(message.content)
                    for num in range(len(human_messages)):
                        print(f"Start 7777777")
                        print(human_messages[num])
                        st.markdown(human_messages[num])
                        print(ai_messages[num])
                        st.markdown(ai_messages[num])
                    #    print(f"End {i}")
                    #    i += 1                    
                else:
                    state["messages"].append(HumanMessage(content=user_input))
                    try:
                        state = buildgraph().invoke(state)
                        print(f"Main: Received Response == {state}")
                        to_display = f"**Agent:** {state["messages"][-1].content}"
                        st.session_state.messages.append(to_display)
                        st.markdown(to_display)
                        st.markdown("---")
                    except Exception as e:
                        st.markdown(f"Error during graph invocation: {e}")
                        st.markdown("---")
    except Exception as e:
        raise
    st.session_state.history["messages"] = state["messages"]
    print(f"State Messages ----> {state["messages"]}")
    print("----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")
 
run_chat()