from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from agent_state import AgentState
from typing import Annotated
import subprocess
from langchain_core.runnables import RunnableConfig
import os
import json

@tool
def execute_aws_command(text: str, config: RunnableConfig):

    """
    Retrieve the parameters and command from State and executed the awscli command

    Args:
        Retrieve the command and arguments from state 

    Returns:
        str: Command output
    """

    # aws_service_values - contains the parameters
    # aws_service_attr - contains the command
    aws_service_attr = config.get("configurable", {}).get("command")
    aws_service_values = config.get("configurable", {}).get("values")

    print(f"State Variables from Tools {aws_service_attr}")
    print(f"Supress from Tools {aws_service_values}")

    print(f"TOOL: suppress_warning: {text}")

    # construct the command to be executed
    service_c = json.loads(aws_service_attr)
    service_d = json.loads(aws_service_values)
    params = ""
    for key, value in service_d.items():
        params= f"{params} {key} {value}"
    final_command = f"{service_c['service_name']} {service_c['command']} {params}"
    #TODO for key, value in my_dict.items():
    #       print(f"Key: {key}, Value: {value}")

    print(f"FIANL COMMAND ----------- {final_command}")
    if state["session_id"] is None or len(state["session_id"]) == 0:
        duration_seconds = 900
        get_session_command = ["aws", "sts", "get-session-token", "--duration-seconds", str(duration_seconds)]
        aws_session_value = json.loads(get_awscli_output(get_session_command, 900))
        aws_session_token = aws_session_value['SessionToken']
        state["session_id"] = aws_session_token
    
    output = get_awscli_output(final_command)
    return output

def get_awscli_output(command):

    #if serial_number and token_code:
    #    command.extend(["--serial-number", serial_number, "--token-code", token_code])
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        credentials = json.loads(result.stdout)["Credentials"]
        print(f"credentials : {credentials}")
        return credentials
    except subprocess.CalledProcessError as e:
        print(f"Error getting AWS session token: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}")
        return None    


def aws_config(aws_session_token, duration_s):
    if aws_session_token is None or len(aws_session_token) == 0:
        get_session_token("", duration_s)
    else:
        return ""

'''
def executeAWSCommandTool() -> str:
    """Execute the command received """
    # List S3 buckets using AWS CLI
    command = 'aws s3 ls'
    try:
        #result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        #result = subprocess.run(['aws', 's3', 'ls', 's3://path/to/my/bucket/12434', '--recursive', '--human-readable', '--summarize'])
        #result = subprocess.run(command, env=env_vars, capture_output=True, text=True, check=True)
        result = subprocess.run([command.split(), env=env_vars, capture_output=True, text=True, check=True])
        print("AWS CLI S3 Buckets:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Stderr: {e.stderr}")

if __name__ == "__main__":
    # This block ensures that main() is called only when the script is run directly.
    aws_session_token=None
    aws_session_token = aws_config(aws_session_token,900)
'''