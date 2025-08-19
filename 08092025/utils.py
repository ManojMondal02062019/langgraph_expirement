import json

def cleanJson(json_content: str):
    if len(json_content) > 0:
        c_json_content = json_content.replace("```json", "")
        c_json_content = c_json_content.replace("```", "")
        return c_json_content
    else:
        return json_content
