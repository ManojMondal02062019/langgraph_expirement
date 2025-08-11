json_response_format_response = {
    "service_name": "ec2",
    "action": "start instance",
    "command": "start-instances",
    "synopsis": "start-instances --instance-ids <value>",
    "options": "--instance-ids (list), --additional-info (string), --dry-run | --no-dry-run (boolean)",
    "global_options": "--debug (boolean), --endpoint-url (string)",
    "required_parameters": "--instance-ids <instance-id>",
    "optional_parameters": "Dry Run"
}

json_response_parameter_response = {
    "--instance-ids": "i-xxxxxxxxxxxxxxxxx",
    "--debug": "false",
    "--dry-run": "true"
}

intent_response_json = {
    "intent": "Params_Collector",
    "mandatory_parameters": {
        "--instance-ids": "i-xxxxxxxxxxxxxxxxx"
    },
    "optional_parameters": {
        "--debug": "false"
    }
}