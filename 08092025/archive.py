from llm_model import llm
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
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        return f"Failed to summarize conversation: {e}"

def save_checkpoint(thread_id, serialize_state):
    print(f"Save History: save checkpoint: Thread={thread_id}")
    try:
        with open(os.path.join(CHECKPOINT_DIR, f"{thread_id}.json"), "w") as f:
            json.dump(serialize_state, f, indent=4)
    except Exception as e:
        print(f"Failed to save checkpoint: {e}")
        return False
    return True

def load_checkpoint(thread_id):
    print(f"Save History: Load checkpoint: Thread={thread_id}")
    path = os.path.join(CHECKPOINT_DIR, f"{thread_id}.json")
    loaded_state_data=None
    try:
        with open(path, "r") as f:
            loaded_state_data = json.load(f)
    except Exception as e:
        print(f"Failed to load checkpoint: {e}")
    print(f"Load History: Result :: {loaded_state_data}")
    return loaded_state_data

def load_checkpoint_bk(thread_id):
    print(f"Save History: Load checkpoint: Thread={thread_id}")
    path = os.path.join(CHECKPOINT_DIR, f"{thread_id}.json")
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