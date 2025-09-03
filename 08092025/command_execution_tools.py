from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from agent_state import AgentState
from typing import Annotated
import subprocess
from langchain_core.runnables import RunnableConfig
import os
import json

@tool
def execute_aws_command(input: str, config: RunnableConfig):

    """
    Retrieve the parameters and command from State and executed the awscli command

    Args:
        Retrieve the command and arguments from state 

    Returns:
        str: Command output
    """

    aws_service_attr = config.get("configurable", {}).get("command")
    aws_service_values = config.get("configurable", {}).get("values")

    # construct the command to be executed
    service_c = aws_service_attr
    print(f"TOOL: Service Command: {str(service_c)}")
    service_d = aws_service_values
    print(f"TOOL: Service Params: {str(service_d)}")
    print(f"TOOL: Service Params TYPE: {type(aws_service_values)}")
    params = ""
    for key, value in service_d.items():
        params= f"{params} {key} {value}"
    final_command = f"aws {service_c['service_name']} {service_c['command']} {params}"

    print(f"TOOL: FINAL COMMAND TO EXECUTE: {final_command}")
    #if state["session_id"] is None or len(state["session_id"]) == 0:
    # get the session_id
    #duration_seconds = 900
    #get_session_command = ["aws", "sts", "get-session-token", "--duration-seconds", str(duration_seconds)]
    #aws_session_value = get_awscli_output(get_session_command)
    #aws_session_token = aws_session_value['SessionToken']
    #print(f"Session Token ::::: {aws_session_value}")
    
    # now execute the command
    output = get_awscli_output(final_command)
    output = output.replace("\n"," ")
    output = output.strip()
    print(f"============== Final Output ========================")
    print(output)
    print(f"============== END Final Output ========================")
    return str(output)

def get_awscli_output(command):
    output_s = ""
    output_e = ""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output_s = json.loads(result.stdout)
        print(f"get_awscli_output :: output : {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error AWS Command: {e}")
        output_e = str(e.stderr)
    except json.JSONDecodeError as e:
        print(f"Error AWS Command JSON: {e}")
        output_e = str(e)
    
    if (len(output_e) > 0):
        #error or exception
        if (len(output_s) > 0):
            return f"Error Code: {output_e}, Error Message: {output_s}"
        else:
            return f"Error Code: {output_e}"
    else:
        #success
        return output_s


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