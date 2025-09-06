import dill
import json
from pathlib import Path

# Create the builder but do not compile it
builder = StateGraph(GraphState)
builder.add_node("increment_count_node", increment_count)
builder.add_conditional_edges("increment_count_node", conditional_end)
builder.add_edge(START, "increment_count_node")

# Save the builder to a file using dill
# Dill is necessary here because the builder contains function references
path = Path("my_graph_builder.dill")
with open(path, "wb") as f:
    dill.dump(builder, f)

print(f"Graph builder saved to {path}")
=======================================================================

# Create a checkpointer instance
checkpointer = MemorySaver()

# Get the internal state of the checkpointer and serialize it to JSON
checkpointer_state_dict = checkpointer.__dict__
path = Path("my_checkpointer_state.json")
with open(path, "w") as f:
    json.dump(checkpointer_state_dict, f)

print(f"Checkpointer state saved to {path}")

===========================

# Load the graph builder
path_builder = Path("my_graph_builder.dill")
with open(path_builder, "rb") as f:
    loaded_builder = dill.load(f)

# Load the checkpointer state and restore it
path_checkpointer = Path("my_checkpointer_state.json")
with open(path_checkpointer, "r") as f:
    checkpointer_state_dict = json.load(f)
    
loaded_checkpointer = MemorySaver()
loaded_checkpointer.__dict__ = checkpointer_state_dict

# Re-compile the graph
loaded_app = loaded_builder.compile(checkpointer=loaded_checkpointer)

print("Graph and checkpointer restored and compiled.")

# Example usage of the restored graph
initial_state = {"current_count": 0, "messages": ["Starting..."]}
result = loaded_app.invoke(initial_state)
print("\nInvoking restored graph:")
print(result)

==================================================================

