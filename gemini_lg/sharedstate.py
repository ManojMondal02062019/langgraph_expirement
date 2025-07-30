from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# This shared GraphState ensures that every node can read/write from the same context.
class GraphState(TypedDict):
messages: Annotated[List[BaseMessage], add_messages]