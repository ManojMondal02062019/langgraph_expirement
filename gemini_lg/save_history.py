from llm_model import invoke_llm_chat
import os
import json
from prompts import summary_prompt
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from typing import Annotated, List

CHECKPOINT_DIR = "./checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def summarize_conversation(messages: List[BaseMessage]) -> str:
    conversation_text = "\n".join([msg.content for msg in messages])
    try:
        response = invoke_llm_chat([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        return f"Failed to summarize conversation: {e}"

def save_checkpoint(thread_id, state):
    print(f"Save History: save checkpoint: Thread={thread_id}, state={state}")
    try:
        if len(state["messages"]):
            #summarized = summarize_conversation(state["messages"])
            #state["messages"] = [HumanMessage(content=f"Summary of previous conversation: {summarized}")]
            for msg in state["messages"]:
                print(f"Message: {msg}")
                print(f"Message dict: {msg.dict()}")

            with open(os.path.join(CHECKPOINT_DIR, f"{thread_id}.json"), "w") as f:
                json.dump([msg.dict() for msg in state["messages"]], f)
    except Exception as e:
        print(f"Failed to save checkpoint: {e}")

def load_checkpoint(thread_id):
    print(f"Save History: Load checkpoint: Thread={thread_id}")
    path = os.path.join(CHECKPOINT_DIR, f"{thread_id}.json")
    print(f"path :: {path}")
    try:
        if os.path.exists(path):
            print("path exists================")
            with open(path, "r") as f:
                print("reading")
                msgs = json.load(f)
                print(f"msgs :: {msgs}")
                messages = [HumanMessage(**m) if m["type"] == "human" else AIMessage(**m) for m in msgs]
                print(f"Save History: Load checkpoint: Messages={messages}")
                return {"messages": messages}
    except Exception as e:
        print(f"Failed to load checkpoint: {e}")
    return {"messages": []}