import json

def cleanJson(json_content: str):
    if len(json_content) > 0:
        c_json_content = json_content.replace("```json", "")
        c_json_content = c_json_content.replace("```", "")
        return c_json_content
    else:
        return json_content

def parseJSONForErrorMessages(json_content: str):
    data = json.loads(json_content)
    print (f"Utils :: {data}")
    content = []
    aws_keys = []
    aws_values = []
    missing_value = ""
    incorrect_value = ""
    for item in data:
        # Iterate over each key-value pair in the dictionary
        if item["value"] is None or len(item["value"]) == 0:
            missing_value = missing_value + item['name'].split()[0] + ", " 
        # Iterate over each key-value pair in the dictionary
        if item["validation_message"] is not None or len(item["validation_message"]) > 0:
            incorrect_value = item['name'].split()[0] + ", "
        
        if item["value"] is not None and item["validation_message"] is not None and item["error_message"] is not None:
            if (len(item["value"])>0 and len(item["validation_message"])==0 and len(item["error_message"])==0):
                aws_keys.append(item['name'].split()[0])
                aws_values.append(item['value'])

    if len(missing_value) > 0:
        content.append("Missing Values: " + missing_value.strip(', '))
    if len(incorrect_value) > 0:
        content.append("Invalid Values: " + incorrect_value.strip(', '))
    
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