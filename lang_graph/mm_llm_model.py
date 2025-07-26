from langchain.chat_models import init_chat_model
from mm_state import AWS_Service, aws_json_schema

#llm_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai").with_structured_output(aws_json_schema)
#llm_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai").with_structured_output(AWS_Service)
llm_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")