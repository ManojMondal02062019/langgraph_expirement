from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.managed.is_last_step import RemainingSteps
from pydantic import BaseModel, Field

import functools
import operator
from typing import Sequence, TypedDict

from langchain_core.messages import BaseMessage

from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent

class State(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


class AWS_Service(BaseModel):
    service_name: str = Field(description="the service name")
    action: str = Field(description="action to be performed")
    command: str = Field(description="cli command to perform the action")
    required_parameters: str = Field(description="required parameters to perform the action")
    optional_parameters: str = Field(description="optional parameters to perform the action")


aws_json_schema = {
    "title": "aws assistant",
    "description": "To help you on the service and action",
    "type": "object",
    "properties": {
        "service_name": {
            "type": "string",
            "description": "Name of the AWS service",
        },
        "action": {
            "type": "string",
            "description": "Action to be performed",
        },
        "command": {
            "type": "string",
            "description": "cli command to perform the action",
        },
        "required_parameters": {
            "type": "string",
            "description": "Required parameters",
        },
        "optional_parameters": {
            "type": "string",
            "description": "Optional parameters",
        }
    },
    "required": ["service_name"],
}

json_response_format_response = {
    "service_name": "ec2",
    "action": "start instance",
    "command": "start-instances",
    "required_parameters": "--instance-ids <instance-id>",
    "optional_parameters": "Dry Run"
}