from llm_model import invoke_llm_chat
import os
from prompts import summary_prompt
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
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
    try:
        if len(state["messages"]):
            #summarized = summarize_conversation(state["messages"])
            #state["messages"] = [HumanMessage(content=f"Summary of previous conversation: {summarized}")]
            with open(os.path.join(CHECKPOINT_DIR, f"{thread_id}.json"), "w") as f:
                json.dump([msg.dict() for msg in state["messages"]], f)
    except Exception as e:
        print(f"Failed to save checkpoint: {e}")

def load_checkpoint(thread_id):
    path = os.path.join(CHECKPOINT_DIR, f"{thread_id}.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                msgs = json.load(f)
                messages = [HumanMessage(**m) if m["type"] == "human" else AIMessage(**m) for m in msgs]
                return {"messages": messages}
    except Exception as e:
        print(f"Failed to load checkpoint: {e}")
    return {"messages": []}