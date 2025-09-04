from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.config import get_store
from validate_tools import validate_params
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver


gem_model_name="gemini-pro"

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
llm_chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
llm_balanced = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)
llm_enhanced = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.6)

#llm_with_tools = llm.bind_tools([executeAWSCommandTool])

memory = InMemorySaver()

agent = create_react_agent(
    model=gem_model_name,
    tools=[validate_params],
    store=get_store 
)