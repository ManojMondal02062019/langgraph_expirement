import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph, chkHumanLoop, checkInterruptFlag, updateStateWithAIMessage
from graphbuild import stateWithAllMessage, checkInterrupts, stateMessagesAndInterrupt, readInterruptMessage
from graphbuild import readAIMessagesFromConfig, readInterruptMessageFromConfig
from graphbuild import set_serialize_state_snapshot, get_serialize_state_snapshot
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command
from langchain_core.messages.utils import filter_messages

thread_id = None

def generate_uuid() -> str:
    return str(uuid.uuid4())

def displayMessageOnly(message, agent_name, color):
    for msg in message:
        to_display = f"**Agent:** {msg}"
        st.session_state.messages.append(to_display)
        if (color == "red"):
            st.markdown(f"<p style='color:red'>**Agent:**</p>",unsafe_allow_html=True)
        elif (color == "blue"):
            st.markdown(f"<p style='color:green'>**Agent:**</p>",unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:violet'>**Agent:**</p>",unsafe_allow_html=True)
        st.markdown(msg)

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

def run_chat(thread_id):
    print("----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    approved_values = ["ok","search","exit", "1", "2", "3"]
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    } 
    if user_input := st.chat_input("You: ", key="my_unique_chat_input_1"):
        state["messages"].append(HumanMessage(content=user_input))
        to_display = f"**User:** {user_input}"
        st.session_state.messages.append(to_display)

        #display old messages
        for message in st.session_state.messages:
            if "AI AWS Assistant" in message:
                st.markdown("<span style='color: #0000FF; font-size: 25px;'>**AI AWS Assistant**</span>", unsafe_allow_html=True)
            elif "Enter 'Old Id: XXXXX' to load previous" in message:
                st.markdown(":orange[**Note - Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query. To save your conversation, enter 'exit', only after compelting the flow.**]") 
            else:
                st.markdown(message)

        chkInterrupt, next_state = checkInterrupts(config)
        to_proceed = False

        if user_input.lower() in ["exit", "quit", "bye"]:
            print (f"Inside exit loop, check Interrupt size : {len(chkInterrupt)}")
            if len(chkInterrupt)>0:
                to_proceed = True
            else:
                #get all the state history to be saved 
                serialize_state = get_serialize_state_snapshot(config)
                file_name = thread_id.replace("-","_")
                check_save = save_checkpoint(file_name, serialize_state)
                if check_save:
                    st.markdown(f"\nConversation Saved. Resume using ID: {file_name}.")
                else:
                    st.markdown(f"\nConversation Save Failed. Please contact administrator.")
                st.markdown("---")
                to_proceed = False
        else:
            to_proceed = True
            
        if to_proceed:
            with st.spinner("Processing..."):   
                if user_input.lower().__contains__("old id"):
                    extract_id = user_input.split(":")
                    file_name_id = extract_id[1].strip()
                    loaded_data = load_checkpoint(file_name_id)
                    set_serialize_state_snapshot(loaded_data, config)
                    st.markdown(f"\nLoaded previous state. You can now continue")
                else:
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

                        if (to_proceed):
                            invokeGraph(buildgraph(), state, True, config, user_input.lower())
                    else:
                        print(f"******* Main: NonInterrupt flow START *******")
                        invokeGraph(buildgraph(), state, False, config, user_input.lower())
                        print(f"******* Main: NonInterrupt flow END *******")

    print("----------------------- E ----------------------------")

# Custom CSS to reduce sidebar width
st.markdown(
    """
    <style>
        [data-testid="stSidebar"][aria-expanded="true"]{
            min-width: 70px;
            max-width: 70px;
        }
        [data-testid="stChatInput"] {
            background-color: #925CC1; /* Light grey background */
            color: #333333; /* Dark grey text */
            caret-color: #333333; /* Cursor color */
        }  
    </style>
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

#st.title(":blue[AI AWS Assistant]")
st.markdown("<span style='color: #0000FF; font-size: 25px;'>**AI AWS Assistant**</span>", unsafe_allow_html=True)
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = {}
    st.session_state.thread_id = generate_uuid()
    st.session_state.index_id = 0
    print(f"THREAD_ID : {st.session_state.thread_id}")
    st.markdown(":orange[**Note - Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query. To save your conversation, enter 'exit', only after compelting the flow.**]") 
    st.session_state.messages.append("Enter 'Old Id: XXXXX' to load previous conversation or proceed with your query. To save your conversation, enter 'exit', only after compelting the flow.")

run_chat(st.session_state.thread_id)