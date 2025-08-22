import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, chkHumanLoop
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command
from itertools import count

thread_id = None
number_id = count(1000)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def run_chat(thread_id):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    if user_input := st.chat_input("You: ", key="my_unique_chat_input_1"):
        state["messages"].append(HumanMessage(content=user_input))
        print(f'*** {next(number_id)} Main: User Input: {user_input}')
        to_display = f"**User:** {user_input}"
        st.session_state.messages.append(to_display)
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
                    # check for fresh response
                    id_number_id = next(number_id)
                    print(f"{id_number_id} ******* Main: NonInterrupt flow")
                    idd = 0
                    for event in buildgraph().stream(state, config, stream_mode="values"):
                        idd = idd + 1
                        print(f" IDDDD -------------------------------------------- {idd}")
                        print(f"** {id_number_id} ********* Main: Event response: {event}")
                        response = buildgraph().get_state(config)
                        #print(f"Current graph state: {response.values}")
                        print(f"** {id_number_id} Main: Next node to execute: {response.next}")
                        #print(f"Main: RESPONSE STATE CONFIG-> {response}")

                        final_output = response.values.get("final_output", "")
                        if len(final_output) > 0:
                            to_display = f"**Agent:** {idd} :: {final_output}"
                            state["messages"].append(AIMessage(content=to_display))
                            st.session_state.messages.append(to_display)
                            st.markdown(to_display)
                            print(f"Completed------ {id_number_id} :: {idd}")
                        else:
                            print(f"{id_number_id} Main final_output else block")
                        
                    # check for interrupts
                    interrupt_id = next(number_id)
                    print(f"{interrupt_id} Main: Check for interrupts")
                    response_interrupt = chkHumanLoop(config, user_input)
                    if (len(response_interrupt) > 0):
                        print(f"{interrupt_id} Main: Inside chkhumanloop")
                        st.markdown(f"**64_Agent:** {response_interrupt}")
                        st.session_state.messages.append(f"**64_Agent:** {response_interrupt}")                        


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