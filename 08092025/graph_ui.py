import traceback
import streamlit as st
import uuid
from archive import load_checkpoint, save_checkpoint
from agent_state import  AgentState         
from langchain_core.runnables import RunnableConfig
from graphbuild import buildgraph
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import StateSnapshot
from langgraph.types import Command

thread_id = None

def generate_uuid() -> str:
    return str(uuid.uuid4())

def checkInterrupts(config):
    print("Inside check Interrupt")
    state_snapshot = buildgraph().get_state(config)
    print(f"Inside state_snapshot ::: {state_snapshot}")
    tool_output = state_snapshot.interrupts        
    if len(tool_output) > 0:
        return (tool_output[0].value).get("text_to_review"), state_snapshot.next
    else:
        return "",""
    
def continueHumanLoop(config, user_input):
    all_field_value_exists = True
    #while all_field_value_exists:
    print("Parameters entries Invoke")
    final_result = buildgraph().invoke(Command(resume=user_input), config=config)
    user_input = None
    print("Parameters entries checkInterrupts")
    chkInterruptMessage2, next_state2 = checkInterrupts(config)
    if (len(chkInterruptMessage2) > 0):
        st.markdown(f"**77_Agent:** {chkInterruptMessage2}")
        st.session_state.messages.append(f"**78_Agent:** {chkInterruptMessage2}")
        print("Still mandatory fields missing***********")
    else:
        all_field_value_exists = False
        print("Exiting as all mandatory fields have values***********")

def run_chat(thread_id):
    print(f"----------------------- S ----------------------------")
    state = {}
    state["messages"] = []
    if user_input := st.chat_input("You: ", key="my_unique_chat_input_1"):
        state["messages"].append(HumanMessage(content=user_input))
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

        print("Line 69")
        chkInterruptMessage, next_state = checkInterrupts(config)
        print(f"InterruptMessage :  {chkInterruptMessage}")
        print(f"Next_State :  {next_state}")
        approved_values = ["approve","modify","rejected"]
        if (len(chkInterruptMessage) > 0):
            print(f"1 user_input :::::::::::::::::::::::::: {user_input}")
            if any(value.lower() in user_input.lower() for value in approved_values):
                print("Check Human Approval")
                final_result = buildgraph().invoke(Command(resume=user_input), config=config)
                #check again if there is any interrupt
                print(f"Check Human Approval Response -- 80 -- {final_result}")
                chkInterruptMessage1, next_state1 = checkInterrupts(config)
                if (len(chkInterruptMessage1) > 0):
                    st.markdown(f"**64_Agent:** {chkInterruptMessage1}")
                    st.session_state.messages.append(f"**64_Agent:** {chkInterruptMessage1}")
                else:    
                    print(f"Approval Final result: {final_result}")        
                    st.markdown(f"**67_Agent:** {final_result["final_output"]}")    
                    st.session_state.messages.append(f"**67_Agent:** {final_result["final_output"]}")
            elif "commandexecute_agent" in next_state:
                    continueHumanLoop(config, user_input)
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
                    for event in buildgraph().stream(state, config, stream_mode="values"):

                        print(f"Event response : {event}")

                        print("*******************************************************************")
                        response = buildgraph().get_state(config)
                        #print(f"Current graph state: {response.values}")
                        #print(f"Next node to execute: {response.next}")
                        print(f" RESPONSE -> {response}")
                        print("*******************************************************************")

                        final_output = response.values.get("final_output", "")
                        if len(final_output) > 0:
                            to_display = f"**Agent:** {final_output}"
                            state["messages"].append(AIMessage(content=to_display))
                            st.session_state.messages.append(to_display)
                            st.markdown(to_display)
                    print("Check Interrupt after event")
                    chkInterruptMessage, next_state = checkInterrupts(config)
                    if (len(chkInterruptMessage) > 0):
                        to_display = chkInterruptMessage
                        st.markdown(f"**IAgent:** {to_display}")
                        st.session_state.messages.append(f"**IAgent:** {to_display}")
                    else:
                        #clear_update_graph_state(config)
                        print("Nothing")

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