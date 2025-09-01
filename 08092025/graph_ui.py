import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, chkHumanLoop, checkInterruptFlag, updateStateWithAIMessage
from graphbuild import stateWithAllMessage, checkInterrupts, stateMessagesAndInterrupt, readInterruptMessage
from graphbuild import readAIMessagesFromConfig, readInterruptMessageFromConfig 
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command
from itertools import count
from langchain_core.messages.utils import filter_messages

thread_id = None
number_id = count(1000)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def displayMessageOnly(message, agent_name, color):
    for msg in message:
        to_display = f"**{agent_name}:** {msg}"
        st.session_state.messages.append(to_display)
        #if (color == "red"):
        #    st.markdown(f":red[{to_display}]")
        #elif (color == "blue"):
        #    st.markdown(f":blue[{to_display}]")
        #else:
        #    st.markdown(to_display)
        st.markdown(to_display)


def invokeGraph(graph, state, resume, config, user_input):
    check_interrupt_in_event = False
    if (resume):
        for event in graph.stream(Command(resume=user_input.lower()), config=config):
            print(f"Main: Interrupt Flow: Event: {event}")
            if "__interrupt__" in event:
                check_interrupt_in_event = True            
        if check_interrupt_in_event:
            print("### Main IF, Interrupt")
            messages = readInterruptMessage(config)
            print(f"Messages Length :: {len(messages)}")
            displayMessageOnly(messages, "Agent1", "red")
        else:
            # let's avoid this
            print("### Main IF, No Interrupt")
            messages = readAIMessagesFromConfig(config)
            displayMessageOnly(messages, "Agent2", "blue")
    else:
        for event in buildgraph().stream(state, config, stream_mode="updates"):
            print(f"Main: NIFlow: Event: {event}")
            if "__interrupt__" in event:
                check_interrupt_in_event = True

        # given preference to interrupt
        if check_interrupt_in_event:
            print("****** Main NIF, Interrupt")
            messages = readInterruptMessage(config)
            displayMessageOnly(messages, "Agent3", "red")
        else:
            print("****** Main NIF, No Interrupt")
            messages = readAIMessagesFromConfig(config)
            displayMessageOnly(messages, "Agent4", "blue")
                        


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


def run_chat(thread_id,interruptFlag):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    approved_values = ["ok","edit","exit", "1", "2", "3"]
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
                    print (f"Main Run: Check interruptFlag : {chkInterrupt}")
                    print (f"Main Run: Check next_state : {next_state}")
                    if (len(chkInterrupt)>0):
                        #check the input values and #lets see the next state
                        to_proceed = True
                        if "human_review_node" in next_state:
                            if any(item == user_input.lower() for item in approved_values):
                                print("Value found! Let's procced..")
                            else:
                                to_proceed = False
                                msg_list = ["Please provide correct value"]
                                displayMessageOnly(msg_list, "AgentN", "")
                        #elif "pre_commandexecute_agent" in next_state:
                        #    print("OR HERE IT COMES")

                        if (to_proceed):
                            invokeGraph(buildgraph(), state, True, config, user_input.lower())
                            #to_proceed
                    else:
                        id_number_id = next(number_id)
                        print(f"{id_number_id} ******* Main: NonInterrupt flow START *******")
                        invokeGraph(buildgraph(), state, False, config, user_input.lower())
                        print(f"{id_number_id} ******* Main: NonInterrupt flow END *******")
                        
                        #if (not interruptFlag):
                        #    print("Main: Agent 4: Getting all the messages to be displayed")
                        #    messages = stateMessagesAndInterrupt(config, False)
                        #    displayMessageOnly(messages, "Agent4")                        

    print(f"{next(number_id)} ----------------------- E ----------------------------")

# Custom CSS to reduce sidebar width
    st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 70px;
           max-width: 70px;
       }
       """,
        unsafe_allow_html=True,
    )   


st.logo("image/aws_logo.png", size="medium", link="https://docs.aws.amazon.com/cli/latest/")

# Sidebar content
with st.sidebar:
    col1, col2, col3, col4, col5 = st.columns(5) # For 3 images
    with col1:
        st.sidebar.image("image/langgraph.png", width=50)
    with col2:
        st.sidebar.image("image/python.png", width=50)
    with col3:
        st.sidebar.image("image/gemini.png", width=50)
    with col4:
        st.sidebar.image("image/chroma.png", width=50)
    with col5:
        st.sidebar.image("image/rag.png", width=50)

st.title("AI AWS Assistant")
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.session_state.thread_id = generate_uuid()
    st.session_state.index_id = 0
    st.interrupt_flag=False
    print(f"THREAD_ID : {st.session_state.thread_id}")
    st.markdown(":orange[Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query]") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query")


run_chat(st.session_state.thread_id, st.interrupt_flag)