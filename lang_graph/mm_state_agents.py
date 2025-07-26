from langgraph.graph import StateGraph, START, END
from langsmith import utils
#from utils import show_graph
from mm_researcher_tool import research_assistant
import uuid
from mm_state import State
from mm_mem import checkpointer, in_memory_store
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

def print_graph(graph):
        
    # Assuming graph has methods or attributes to access nodes and edges
    nodes = graph.nodes  # Adjust according to actual method/attribute to access nodes
    edges = graph.edges  # Adjust according to actual method/attribute to access edges

    print("Nodes:")
    for node in nodes:
        print(f"  {node}")

    print("\nEdges:")
    for edge in edges:
        print(f"  {edge[0]} -> {edge[1]}")


class Assistant:

    def __init__(self):
        self.aws_assistant_workflow = StateGraph(State)
        self.aws_assistant_workflow.add_node("research_assistant", research_assistant)
        self.aws_assistant_workflow.add_edge(START, "research_assistant")
        self.aws_assistant_workflow.add_edge("research_assistant", END)
        self.research_graph = self.aws_assistant_workflow.compile()

        # Compile the graph with checkpointer for short-term memory and store for long-term memory
        self.aws_assist_subagent = self.aws_assistant_workflow.compile(
            name="aws_assist_subagent", 
            checkpointer=checkpointer, 
            store=in_memory_store
        )
        app_graph = self.research_graph.get_graph(xray=True) 
        print_graph(app_graph)
        app_graph.print_ascii()

    def assistant_graph(self):
        return self.research_graph

    def sub_assistant_graph(self):
        return self.aws_assist_subagent

    def invoke_assistant(self, user_prompt_messaage:str):

        # Invoke the music catalog subagent with the user's question
        # The agent will use its tools to search for Rolling Stones music and provide recommendations
        return self.aws_assist_subagent.invoke(user_prompt_messaage)

        # Display all messages from the conversation in a formatted way
        #for message in result["messages"]:
        #message.pretty_print()