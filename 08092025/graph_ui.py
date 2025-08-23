import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, chkHumanLoop, checkInterruptFlag, updateStateWithAIMessage, stateWithAllMessage
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command
from itertools import count

thread_id = None
number_id = count(1000)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def displayMessage(config):
    event = buildgraph().get_state(config)
    if "messages" in event and event["messages"]:
        last_message = event["messages"][-1]
        print(f"Main Run: displayMessage: Last message in stream : {last_message.content}")
        to_display = f"**Agent:** {last_message.content}"
        state["messages"].append(AIMessage(content=to_display))
        st.session_state.messages.append(to_display)
        st.markdown(to_display)
        print(f"Main Run: Completed------")
    else:
        print(f"Main Run: No RESPONSE")


def runInterruptLogic(config, user_input):
    # check for interrupts
    print(f"Main: runInterruptLogic: Checking for interrupts")
    response_interrupt = chkHumanLoop(config, user_input)
    if (len(response_interrupt) > 0):
        displayMessage(config)

def run_chat(thread_id):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    } 
    if user_input := st.chat_input("You: ", key="my_unique_chat_input_1"):
        state["messages"].append(HumanMessage(content=user_input))
        print(f'*** {next(number_id)} Main: User Input: {user_input}')
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
                    print ("Main Run: Check for any interruptions...")
                    chkInterrupt = checkInterruptFlag(config)
                    if (chkInterrupt is None or chkInterrupt == False):
                        # check for fresh response
                        id_number_id = next(number_id)
                        print(f"{id_number_id} ******* Main: NonInterrupt flow")
                        idd = 0
                        for event in buildgraph().stream(state, config, stream_mode="values"):
                            displayMessage(config)

                        print("Main Run: Check Interrupts after final output")
                        runInterruptLogic(config, user_input)
                    else:
                        print("Run Interrupts only")
                        runInterruptLogic(config, user_input)   

    #updateStateWithAIMessage(config, "Hi.....s")      
    #stateWithAllMessage(config)
    print(f"{next(number_id)} ----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.session_state.thread_id = generate_uuid()
    st.session_state.index_id = 0
    print(f"THREAD_ID : {st.session_state.thread_id}")
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")


run_chat(st.session_state.thread_id)