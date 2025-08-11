from typing import TypedDict

class AWSServiceAttributes(TypedDict, total=False):
    service_name: str
    action: str
    command: str
    synopsis: str
    options: str
    global_options: str
    required_parameters: str
    optional_parameters: str