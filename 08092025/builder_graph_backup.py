    # Define tools and bind them to model
    #tools = [validate_params]
    #model_with_tools = llm().bind_tools(tools, parallel_tool_calls=False)
    builder = StateGraph(AgentState)
    builder.add_node("chat_agent", chat_agent)
    builder.add_node("intent_agent", intent_agent)
    builder.add_node("identifyservice_agent", identifyservice_agent)
    builder.add_node("commandexecute_agent", commandexecute_agent)
    builder.add_node("human_review_node", human_approval)
    #builder.add_node("approved_intent_path", approved_node)
    #builder.add_node("rejected_intent_path", rejected_node)
    #builder.add_node("modify_intent_path", modify_node)
    builder.add_node("route", lambda x: x)
    
    # commented on 08162025
    builder.add_conditional_edges("route", route, {
        "chat_agent": "chat_agent",
        "intent_agent": "intent_agent"
    })

    builder.set_entry_point("route")
    builder.add_edge("chat_agent", END)
    builder.add_edge("intent_agent", "identifyservice_agent")
    builder.add_edge("identifyservice_agent", "human_review_node")
    #builder.add_edge("approved_path", "commandexecute_agent")
    #builder.add_edge("modify_path", "identifyservice_agent")
    #builder.add_edge("rejected_path", END)
    #builder.add_edge("commandexecute_agent", END)

    try:
        graph = builder.compile(checkpointer=memory)     
    except Exception as e:
        raise RuntimeError(f"Failed to compile LangGraph: {e}")
