import streamlit as st
import uuid
from mm_state_agents import Assistant
from mm_utils import parse_langgraph_output
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

def generate_uuid() -> str:
    return str(uuid.uuid4())

assistant = Assistant()
uuid = generate_uuid

st.title("AI AWS Assistant")

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AWS Assistant. How can we assist you today?"}
    ]

# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("Your question"):
  
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        #start_time = time.time()
        #logging.info("Generating response...")
        with st.spinner("Processing..."):        
            inputs = {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ],
            }
            config = {"configurable": {"thread_id": uuid, "recursion_limit": 2}} 
            final_event = None
            for step in assistant.assistant_graph().stream(inputs, config=config):
                print(f"STEP ::::::::::: {step}")
            
                response_message=parse_langgraph_output(step)
          
                for agent, content in response_message:

                    assistant_reply = f"**Agent:** `{agent}`\n\n{content}"
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    st.markdown(assistant_reply)
                    st.markdown("---")            
