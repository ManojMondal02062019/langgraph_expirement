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
    "instance-ids": "i-xxxxxxxxxxxxxxxxx",
    "validation_message": "Your instance id format is good",
    "error_message": "Kindly provide value for instance-ids"
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

json_final_response_pre_command = [
  {
    "name" : "--instance-ids <value>",
    "value": "i-xxxxxxxxxxxxxxxxx",
    "format": "string",
    "validation_message": "",
    "error_message": ""
  }
]

example_1 = {
            "name" : "instance-ids",
            "value": "i-xxxxxxxxxxxxxxxxx",
            "format": "string",
            "validation_message": "",
            "error_message": ""
        }

example_2 = {
            "name" : "instance-ids",
            "value": "i-xxxxxxxxxxxxx",
            "format": "string",
            "validation_message": "The instance id should be of 16 character, prefixed by -i",
            "error_message": ""
        }

example_3 = {
            "name" : "instance-ids",
            "value": "i-xxxxxxxxxxxxx",
            "format": "string",
            "validation_message": "The instance id should be of 16 character, prefixed by -i",
            "error_message": "Please provide value for instance-ids"
        }