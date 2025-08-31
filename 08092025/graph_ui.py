import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, chkHumanLoop, checkInterruptFlag, updateStateWithAIMessage
from graphbuild import stateWithAllMessage, checkInterrupts, stateMessagesAndInterrupt, readInterruptMessage
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command
from itertools import count
from langchain_core.messages.utils import filter_messages

thread_id = None
number_id = count(1000)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def displayMessageOnly(message, agent_name):
    if (agent_name == "Agent22"):
        print(f"MMMMMMMMMSSSSSSSSSS {message}")
    inde = 1
    message = [s for s in message if s != '']
    for msg in message:
        if (agent_name == "Agent22"):
            print(f"{inde} MMSSGG Inside {msg}")
            inde = inde+1
        to_display = f"**{agent_name}:** {msg}"
        st.session_state.messages.append(to_display)
        st.markdown(to_display)


def displayMessageFromObject(config, event, state):
    if (config is not None): 
        event = (buildgraph().get_state(config)).values
        print(f"Config is not none, config event ::::: {str(event)}")
        ai_messages = filter_messages(event["messages"], include_types=["ai"])
        print(f"Main: displayMessage: ai response: {ai_messages}")
        last_response = ""
        if (len(ai_messages) > 0):
            last_response = (ai_messages[len(ai_messages)-1])
            print(f"Main: displayMessage: ai response: {last_response}")
        else:
            print("No AI response")
    elif (event is not None):
        print("Event is not none")
        if "messages" in event and event["messages"]:
            last_message = event["messages"][-1]
            print(f"Main Run: Last message in stream : {last_message.content}")
            #displayMessageOnly(last_message.content, state)
            to_display = f"**#####Agent:** {last_message.content}"
            state["messages"].append(AIMessage(content=to_display))
            st.session_state.messages.append(to_display)
            st.markdown(to_display) 

            print(f"Main Run: Completed------------")
        else:
            print(f"Main Run: No RESPONSE")
    else:
        print("No config, no event")        

def runInterruptLogic(config, user_input):
    # check for interrupts
    print(f"Main: runInterruptLogic: Checking for interrupts")
    response_interrupt = chkHumanLoop(config, user_input)
    if ((response_interrupt is not None) and (len(response_interrupt) > 0)):
        for msg in response_interrupt:
            print(f"Main: runInterruptLogic: After human loop ::::::::::::::::::: {msg}")
            if (len(msg) > 0):
                displayMessageOnly(msg)
    else:
        pass

def run_chat(thread_id,interruptFlag):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    approved_values = ["ok","modify","end", "1", "2", "3"]
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
                    chkInterrupt, next_state = checkInterrupts(config)
                    print (f"Main Run: Checking interruptFlag : {chkInterrupt}")
                    print (f"Main Run: Checking next_state : {next_state}")
                    if (len(chkInterrupt)>0):
                        #check the input values and #lets see the next state
                        to_proceed = True
                        if "human_review_node" in next_state:
                            if any(item == user_input.lower() for item in approved_values):
                                print("Value found!")
                            else:
                                to_proceed = False
                                msg_list = ["Please provide correct value"]
                                displayMessageOnly(msg_list, "AgentN")
                        elif "pre_commandexecute_agent" in next_state:
                            print("OR HERE IT COMES")

                        
                        if (to_proceed):
                            for event in buildgraph().stream(Command(resume=user_input.lower()), config=config):
                                print(f"=============================={event}")
                                if "__interrupt__" in event:
                                    msg = "******Graph interrupted! Awaiting human input."
                                    print(msg)
                                    messages = readInterruptMessage(config)
                                    displayMessageOnly(messages, "Agent1")
                                    interruptFlag = True
                                    print("BREAK")
                                    break
                                else:
                                    # let's avoid this
                                    messages = stateMessagesAndInterrupt(config, False)
                                    displayMessageOnly(messages, "Agent22")

                                    print("HERE it should come")
                    else:
                        id_number_id = next(number_id)
                        print(f"{id_number_id} ******* Main: NonInterrupt flow START *******")
                        for event in buildgraph().stream(state, config, stream_mode="updates"):
                            print(f"Agent3 : Event: {event}")
                            if "__interrupt__" in event:
                                print("****** Main Interrupted! Awaiting human input.")
                                messages = readInterruptMessage(config)
                                displayMessageOnly(messages, "Agent3")
                                interruptFlag = True
                                break
                            else:
                                interruptFlag = False
                                print(f"Main Not Interrupted: Event (not printed in UI) ...")
                        print(f"{id_number_id} ******* Main: NonInterrupt flow END *******")
                        
                        if (not interruptFlag):
                            print("Main: Agent 4: Getting all the messages to be displayed")
                            messages = stateMessagesAndInterrupt(config, False)
                            displayMessageOnly(messages, "Agent4")                        

    print(f"{next(number_id)} ----------------------- E ----------------------------")

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.session_state.thread_id = generate_uuid()
    st.session_state.index_id = 0
    st.interrupt_flag=False
    print(f"THREAD_ID : {st.session_state.thread_id}")
    st.markdown("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")


run_chat(st.session_state.thread_id, st.interrupt_flag)