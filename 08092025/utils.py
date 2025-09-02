import math
import json 
import re
import ast

def cleanJson(json_content: str):
    if len(json_content) > 0:
        c_json_content = json_content.replace("```json", "")
        c_json_content = c_json_content.replace("```", "")
        return c_json_content
    else:
        return json_content

def parseJSONForErrorMessages(json_content: str):
    # dumping again in case json_content single string
    dump1 = json.dumps(ast.literal_eval(json_content))
    data = json.loads(dump1)
    print (f"Utils :: data :: {data}")
    content = []
    aws_keys = []
    aws_values = []
    missing_value = ""
    incorrect_value = ""
    for item in data:
        # Iterate over each key-value pair in the dictionary
        if item['value'] is None or bool(re.match(r"<.*?>", item['value'])) or bool(re.match(r"[.*?]", item['value'])) or len(item['value'].strip()) == 0 or "xxxx" in item['value']:
            # value does not exists
            missing_value = missing_value + item['name'].split()[0] + ", " 
            item['value']=""
        else:
            # value exists
            # Iterate over each key-value pair in the dictionary
            if item['validation_message'] is not None and len(item['validation_message']) > 0:
                # add a special check for number format,
                # as the data is enclosed within quotes.
                if str(item['format']) == "number":
                    if not item['value'].isnumeric():
                        incorrect_value = item['name'].split()[0] + ", "
                        item['value']=""
                    else:
                        item['validation_message'] = ""
                else:
                    incorrect_value = item['name'].split()[0] + ", "
                    item['value']=""

        if (len(item['value']) >0 and len(item['validation_message'])==0 and len(item['error_message'])==0):
            aws_keys.append(item['name'].split()[0])
            aws_values.append(item['value'])

    if len(missing_value) > 0:
        content.append("Missing Values: " + missing_value.strip(', '))
    if len(incorrect_value) > 0:
        content.append("Invalid Values: " + incorrect_value.strip(', '))
    
    print(f"Content:: {content}")
    print(f"Content Keys :: {aws_keys}")
    print(f"Content Values:: {aws_values}")
    return content,aws_keys,aws_values

def parseJSONForKeysValues(json_content: str):
    data = json.loads(json_content)
    print (f"Utils :: {data}")
    content = []
    for item in data:
        # Iterate over each key-value pair in the dictionary
        status = item['error_message'] if len(item['error_message']) > 0 else ""
        status1 = item['validation_message'] if len(item['validation_message']) > 0 else ""

        if len(status) > 0 or len(status1) > 0:
            str= status + ',' + status1
            str = str.strip(',')
            content.append(str)
    return content    