from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.config import get_store

@tool
def validate_params(config: RunnableConfig) -> str:
    """
    This tool will be used to validate all the mandatory parameters are provided by user to run a command.

    Args:
        state: so that the conversation history can be used to lookup any mandatory parameter

    Returns:
        str: response to continue asking for mandatory parameters, until it's completed
    """    
    """Look up user info."""
    # Same as that provided to `builder.compile(store=store)`
    # or `create_react_agent`
    store = get_store()
    user_id = config["configurable"].get("user_id")
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"