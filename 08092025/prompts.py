from jsonresponse import json_response_format_response, json_response_parameter_response, example_1, example_2, example_3, example_4, example_5, json_final_response_pre_command

intent_prompt = """
    You are an Assistant in identifying the intent of the user request. 
    If the user request intent is clear in identifying the respective AWs Service and command, then proceed with next steps.
    Interrupt the user until you are clear on what AWS service and features and command the user requires help.
    Classify the user's request as one of the following:
    - identifyservice_agent - Identify_AWS_Service, if intent is clear to identify the AWS service and command
    - commandexecute_agent - Execute_Command, if we need to execute the command
    Only output the label.
    
    """

#define system prompt for tool calling agent
system_prompt = """ 
        You are an AWS assistant.
        Use tools to answer questions or for executing the command. If you do not have a tool then ignore it and answer accordingly.
    """

identify_service_prompt = f"""
        You are an AWS assistant and provide only the AWS Service Name and action extracted from user prompt.
        Only return the Service Name, action, command, required and optional parameters. 
        The response should be very concise.
        The response should be very concise and follow the below points while generating the response
        - Strictly adhere to the described {json_response_format_response} schema in the response.
        - JSON, keys and values require double-quotes
        - Do not wrap the json codes in JSON markers
    """

identify_service_prompt_1 = f"""
    You are an AWS cloud agent which should always use best search engine (either google or Bing) and 
    get best search results to generate response. 
    - You need to understand the user input #human_message#.
    - The user request should be searched using search engine AND related to AWS Services.
    - Search or Find full details on the user requested AWS service and action requested in #human_message# request.
    - Read the Command, Required Parameters, Optional Parameters, Example for executing the user request.
    - Read the Prerequisites, Steps to generate response.
    - Generate response as AWSCLI CODE to execute and NOT as AWS Management Console.

    The response should be very concise and should be answered in {json_response_format_response} format. 
    We don't want markdown in our output
    - return the data in a JSON code block without a language tag.
    - JSON, keys and values require double-quotes
    """

router_prompt = """

    You are a routing assistant and take decision on user input whether to route to intent_agent or chat_agent.
    If user input is related to ongoing conversations then please use the ongoing intent and don't change it.
    If user input is related to AWS services and features, use intent_agent
    If user response is realted to Interrupt and Resume then please use intent_agent
    If user input is NOT above and is a generic input then ONLY use chat_agent.
    The user's message as either
    - intent_agent: if the request is related to AWS Cloud Services, features and executing aws commands. 
    - chat_agent: if the user response is NEW conversation and related to general topic, non-aws related. 
    If the user response is related to answers asked from old conversation OR from interruptions or Resume, 
    then route it to intent_agent as per the flow. 
    Check the graph flow and from where the Interupt or Resume are invoked.
    Respond then with the label: intent_agent or chat_agent.
    Note - Please check the interruptions and resume flow accordingly as from which node or agent it got invoked.

"""    

summary_prompt = """

    Summarize chat from history. Remove duplicates, preserve messages having values.
    Consider the latest values for the variables or parameters. Discard the old values.

"""    

command_pre_service_prompt = f"""
        You are an expert at extracting information. 
            - Please ensure that you have the values for all parameters marked as 'required' from #params#. 
            - Please ensure that you have the valid values for the required and optional mentioned in #params#. 
            - Check the Human messages, conversation history to extract the values for required and optional
            parameters from #human#. 
            - If value are found for the required paramters and is relevant for the command, then use it and 
            not ask it again from user. Example - To retrieve information you can reuse existing values but for 
            creating new resource you cannot use existing values. Think thoughtfully to use existing values.
            - Return the parameters whose values are having invalid format. It should compy with parameter 
            format value. If it's boolean format then it should have true or false, 
            If int or integer or number, then it should have numbers only.
        
        The response should be very concise and follow the below points while generating the response
            - Strictly adhere to the this format as response. {json_final_response_pre_command}
            - In the {json_final_response_pre_command} structure if any of the parameter value is found, then display it
            - JSON, keys and values require double-quotes
            - Do not wrap the json codes in JSON markers

        Examples: the same response format shall be produced for all required parameters and for optional parameters if provided
        1. For a valid value, the response should be like this = {example_1}

        2. For a invalid instance-ids value, the response should be like this = {example_2}

        3. If instance-ids value does not exists, the response should be like this = {example_3}

        4. If version value does not have number format, the response should be like this = {example_4}

        4. If not a required parameter and is optional, then the response should be like this = {example_5}

    """

command_join_validation_error_prompt = f"""
    Write a concise summary of the following ##.
    The response should be very concise and follow the below points while generating the response - 
    - Please provide values or correct format for the following required fields (as comma seperated)
"""

command_join_validation_error_prompt_worked_1 = f"""
    Write a concise summary from the following message - ##.
    The response should be very concise and ONLY return the parameters (as comma seperated).
"""