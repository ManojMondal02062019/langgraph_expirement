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