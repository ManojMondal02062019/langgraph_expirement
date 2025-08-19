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

        chkInterruptMessage, next_state = checkInterrupts(config)
        print(f"InterruptMessage :  {chkInterruptMessage}")
        print(f"Next_State :  {next_state}")
        approved_values = ["approve","modify","rejected"]
        if (len(chkInterruptMessage) > 0):
            if any(value.lower() in user_input.lower() for value in approved_values):
                print("Human Approval")
                final_result = buildgraph().invoke(Command(resume=user_input), config=config)
                print(f"Approval Final result: {final_result}")        
                st.markdown(f"**Agent:** {final_result["final_output"]}")    
            elif "commandexecute_agent" in next_state:
                print("Parameters enries")
                final_result = buildgraph().invoke(Command(resume=user_input), config=config)
                print(f"Command Final result: {final_result}")        
                st.markdown(f"**Agent:** {final_result["final_output"]}")    
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
                    chkInterruptMessage, next_state = checkInterrupts(config)
                    if (len(chkInterruptMessage) > 0):
                        to_display = chkInterruptMessage
                        st.markdown(to_display)
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