import streamlit as st
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())

def run_chat():
    try:
        thread_id = input("Enter chat ID (or press enter to start new): ").strip()
        if not thread_id:
            thread_id = os.urandom(4).hex()
            print(f"🆕 New conversation started: {thread_id}")
        else:
            print(f"🔁 Resuming conversation: {thread_id}")

        state = load_checkpoint(thread_id)

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                save_checkpoint(thread_id, state)
                print(f"\n💾 Saved. Resume using ID: {thread_id}")
                break

            state["messages"].append(HumanMessage(content=user_input))
            try:
                state = graph.invoke(state)
                print("\nAI:", state["messages"][-1].content)
            except Exception as e:
                print(f"⚠️ Error during graph invocation: {e}")

    except Exception as e:
        print(f"❌ Critical error: {e}")


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
        ##start_time = time.time()
        logging.info("Generating response...")
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
            for step in assistant.stream(inputs, config=config):
                final_event = step  # Keep updating to the latest step
                print(final_event)
            
                response_message=parse_langgraph_output(final_event)
          
                for agent, content in response_message:

                    assistant_reply = f"**Agent:** `{agent}`\n\n{content}"
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    st.markdown(assistant_reply)
                    st.markdown("---")            
