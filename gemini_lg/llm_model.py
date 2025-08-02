from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
#from langchain.chat_models import init_chat_model

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
#llm_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

def invoke_llm_prompts(system_prompt,user_msg):
    print(f"Model System_Prompt :: {system_prompt}")
    print(f"Model User Message :: {user_msg}")
    if system_prompt and user_msg:
        intent = llm.invoke([HumanMessage(content=system_prompt), HumanMessage(content=user_msg)])
    elif user_msg:
        intent = llm.invoke(user_msg)
    print(f"LLM Model Intent :::: {intent}")
    return intent


def invoke_llm_chat(messages):
    return llm.invoke(messages)