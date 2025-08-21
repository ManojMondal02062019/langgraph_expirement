from jsonresponse import json_response_format_response, json_response_parameter_response, example_1, example_2, example_3, example_4, json_final_response_pre_command

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
        Only return the Service Name, action, command, required and optional parameters. The response should be very concise.
        The response should be very concise and follow the below points while generating the response
        - Strictly adhere to the described {json_response_format_response} schema in the response.
        - JSON, keys and values require double-quotes
        - Do not wrap the json codes in JSON markers
    """

identify_service_prompt_1 = f"""
    You are an AWS cloud agent which uses website https://docs.aws.amazon.com/cli/latest/reference/#available-services.
    to understand the user input and extract the AWS Service Name and actions associated with it. 
    NOTE - Do not include response from SDK nor from REST API nor from boto3. ONLY refer to cli documentation.
    You are required to 
    - understand the user message and extract the AWS service name.
    - understand the command or action from the user message and find the available methods that can be used to run the action 

    Think again and respond with below details.
    - AWS Service Name, 
    - action, 
    - command, 
    - all the required parameters,
    - all optional parameters,
    - Synopsis,
    - Options,
    - Global Options.
    The response should be very concise. 
    The output should be as per this example {json_response_format_response}.
    We don't want markdown in our output
    - return the data in a JSON code block without a language tag.
    - JSON, keys and values require double-quotes
    """

router_prompt = """

    You are a routing assistant and take decision on user input and current conversation history, to classify 
    the user's message as either
    - intent_agent: if the request is related to AWS Cloud Services, features and executing aws commands
    - chat_agent: for anything else (general conversation, non-aws related)
    Respond with only the label: intent_agent or chat_agent

"""    

summary_prompt = """

    Summarize chat from history. Remove duplicates, preserve messages having values.

"""    

command_pre_service_prompt = f"""
        You are an expert at extracting information. 
        Please ensure that you have all the required values for required_parameters mentioned in  #params#. 
        Please extract the information from the conversation history or from the following text #human#.
        Also please check message, history, conversation to find in case value for these parameters is already provided.
        If value are found for the required paramters, then use it and not ask it again from user.
        Kindly return the required_parameters if values are found in conversation history. Also return the parameters whose values 
        are having invalid format. It should compy with parameter format value. If it's boolean format then it should have true or false, 
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