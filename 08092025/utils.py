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
    for item in data:
        # Iterate over each key-value pair in the dictionary
        status = item['error_message'] if len(item['error_message']) > 0 else ""
        status1 = item['validation_message'] if len(item['validation_message']) > 0 else ""

        if len(status) > 0 or len(status1) > 0:
            content.append(f"{status}, {status1}")
    return content