from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
#from langchain.chat_models import init_chat_model

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
#llm_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

def invoke_llm_prompts(system_prompt: str, user_msg: str):
    intent=""
    if system_prompt and user_msg:
        intent = llm.invoke([HumanMessage(content=system_prompt), HumanMessage(content=user_msg)]).content.strip()
    elif user_msg:
        intent = llm.invoke(user_msg).content
    return intent

def invoke_llm_chat(messages):
    return llm.invoke(messages)