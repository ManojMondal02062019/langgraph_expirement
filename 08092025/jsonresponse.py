json_response_format_response = {
    "service_name": "ec2",
    "action": "start instance",
    "command": "start-instances",
    "synopsis": "start-instances --instance-ids <value>",
    "options": "--instance-ids (list), --additional-info (string), --dry-run | --no-dry-run (boolean)",
    "global_options": "--debug (boolean), --endpoint-url (string)",
    "required_parameters": "--instance-ids <instance-id>",
    "optional_parameters": "Dry Run",
    "awscli_command": "aws ec2 start-instances --instance-ids (list); aws ec2 describe-instances --instance-ids (string))"
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
    "error_message": "",
    "mandatory": "Yes"
  }
]

example_1 = {
            "name" : "instance-ids",
            "value": "i-000760dffa1b3b4a9",
            "format": "string",
            "validation_message": "",
            "error_message": "",
            "mandatory": "Yes"
        }

example_2 = {
            "name" : "instance-ids",
            "value": "i-000760dff",
            "format": "string",
            "validation_message": "The instance id should be of total 19 character including prefixed by -i",
            "error_message": "",
            "mandatory": "Yes"
        }

example_3 = {
            "name" : "instance-ids",
            "value": "i-xxxxxxxxxxxxx",
            "format": "string",
            "validation_message": "",
            "error_message": "Please provide value for instance-ids",
            "mandatory": "Yes"
        }

example_4 = {
            "name" : "version",
            "value": -1.1,
            "format": "number",
            "validation_message": "The version should be a positive number",
            "error_message": "",
            "mandatory": "Yes"
        }

example_5 = {
            "name" : "SecurityGroup",
            "value": "sg-xxxxxxx",
            "format": "string",
            "validation_message": "",
            "error_message": "",
            "mandatory": "No. If already exists, will use it else please provide it"
        }

example_6 = {
            "name": "instance-id",
            "existing_value": "i-1223"
        }

example_7 = {'--instance-ids': 'i-000760dffa1b3b4a9', '--dry-run': 'False' }
example_8 = {'--instance-ids': 'i-000760dffa1b3b4a8', '--dry-run':'False'}
example_9 = {'--instance-ids': 'i-000760dffa1b3b4a8', '--dry-run':'False', '--ami-id': 'ami-000760dffa1'}