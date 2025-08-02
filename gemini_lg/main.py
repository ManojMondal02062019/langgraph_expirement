from save_history import load_checkpoint, save_checkpoint
import os
from langchain_core.messages import HumanMessage, SystemMessage


def run_chat():
    try:
        thread_id = input("Enter chat ID (or press enter to start new): ").strip()
        if not thread_id:
            thread_id = os.urandom(4).hex()
            print(f"New conversation started: {thread_id}")
        else:
            print(f"Resuming conversation: {thread_id}")

        state = load_checkpoint(thread_id)

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                save_checkpoint(thread_id, state)
                print(f"\nSaved. Resume using ID: {thread_id}")
                break

            state["messages"].append(HumanMessage(content=user_input))
            try:
                state = graph.invoke(state)
                print("\nAI:", state["messages"][-1].content)
            except Exception as e:
                print(f"Error during graph invocation: {e}")

    except Exception as e:
        print(f"Critical error: {e}")


if __name__ == "__main__":
    print("LangGraph Chatbot (Gemini + GitHub Agent with Routing)")
    run_chat()

====================================================================================================
import streamlit as st
import uuid
from graphbuild import buildgraph
from langchain_core.messages import HumanMessage
from save_history import load_checkpoint, save_checkpoint

def generate_uuid() -> str:
    return str(uuid.uuid4())

def run_chat():
    try:
        if prompt := st.chat_input("Enter chat ID (or press write 'start new'): "):
            if 'start new' not in prompt:
                thread_id = prompt
            else:
                thread_id = ''

            if not thread_id:
                thread_id = generate_uuid()
                st.markdown(f"New conversation started: {thread_id}")
            else:
                st.markdown(f"Resuming conversation: {thread_id}")
            st.markdown("---")

            state = load_checkpoint(thread_id)

            while True:
                if user_input := st.chat_input("\nYou: "):
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        save_checkpoint(thread_id, state)
                        st.markdown(f"\nSaved. Resume using ID: {thread_id}")
                        st.markdown("---")
                        break

                    state["messages"].append(HumanMessage(content=user_input))
                    try:
                        state = buildgraph.invoke(state)
                        st.markdown("\nAI:", state["messages"][-1].content)
                        st.markdown("---")
                    except Exception as e:
                        st.markdown(f"Error during graph invocation: {e}")
                        st.markdown("---")
    except Exception as e:
        st.markdown(f"Critical error: {e}")
        st.markdown("---")            

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AWS Assistant. How can we assist you today?"}
    ]
# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])    
run_chat()   