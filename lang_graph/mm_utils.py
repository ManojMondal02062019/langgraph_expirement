from langchain_core.messages import HumanMessage,AIMessage
import json

def parse_langgraph_output(stream):
    print(f"stream Data : {stream}")
    print(f"stream items : {stream.items()}")
    print(f"stream Data : {stream['research_assistant']}")
    print(f"stream Data : {stream['research_assistant']['messages']}")
    json_output=json.dumps(stream['research_assistant']['messages'], indent=4)
    #print(f"stream Data : {stream['research_assistant']['messages']['service_name']}")
    results = []
    i = 0
    for key, value in stream.items():
        print(f"Index: {i+1}")
        print(f"Key : {key}")
        print(f"Value : {value}")
        if key == "supervisor":
            continue
        print(f'Value Messages ::: {value['messages']}')
        data_dict = json.loads(json.dumps(value['messages']))
        print(f'Value O Messages ::: {data_dict}')
        val = "service name: " + (data_dict[0]['service_name']) +  " and action is " + (data_dict[0]['action'])
        results.append((key, val))
        #for msg in messages:
        #    if isinstance(msg, str):
        #        results.append((key, msg))
        #    elif isinstance(msg, AIMessage):
        #        results.append((key, msg.content))
    
    print(f"RESULTS ::: {results}")
    return results