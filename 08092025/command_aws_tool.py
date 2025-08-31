from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from agent_state import AgentState
from typing import Annotated
import subprocess
from langchain_core.runnables import RunnableConfig
import os
import json

@tool
def execute_aws_command_for_config(input: str, config: RunnableConfig):

    """
    Execute script to check if aws is correctly configured

    Args:
        Retrieve the command and arguments from state 

    Returns:
        str: Command output
    """

    command_to_run = config.get("configurable", {}).get("command")
    print(f"TOOL: FINAL COMMAND TO EXECUTE: {command_to_run}")

    # now execute the command
    output = get_awscli_output(final_command)
    output = check_exact_type(output)
    print(f"============== Final Output ========================")
    print(output)
    print(f"============== END Final Output ========================")
    return str(output)

def check_exact_type(obj):
    if type(obj) is str:
        obj.replace("\n"," ")
        obj.strip()
    print(f"Inside object type check: {type(obj)}")
    return obj

def get_awscli_output(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        print(f"get_awscli_output :: output : {output}")
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error AWS Command: {e}")
        return e.stderr
    except json.JSONDecodeError as e:
        print(f"Error AWS Command JSON: {e}")
        return (f"Error parsing JSON output: {e}")    


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