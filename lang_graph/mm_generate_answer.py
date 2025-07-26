import logging
from fastapi import APIRouter, Depends, HTTPException, status
from models.generate_answer import ErrorResponse, GenerationRequest, GenerationResponse
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse, StreamingResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter()
graph = build_graph()
logging.info('Loaded graph')

@router.post("/generate-stream/", response_class=GenerationResponse)
async def generation_streaming(request: GenerationRequest,thread_id: str = Header('111222', alias="X-THREAD-ID")):
    query = request.query
    logging.info(f'Received the Query - {query} & thread_id - {thread_id}')
    inputs = [
        HumanMessage(content=query)
    ]
    state = {'messages': inputs}
    config = {"configurable": {"thread_id": thread_id, "recursion_limit": 2}}  
#    response = graph.invoke(input=state,config=config)
    logging.info('Generated Answer from Graph')
#    dialog_states = response['dialog_state']
#    dialog_state = dialog_states[-1] if dialog_states else 'primary_assistant'
    
#    messages = response['messages'][-1].content

    #return GenerationResponse(answer="My answer is blah blah blah",dialog_state="primary_assistant")    
    return JSONResponse({
        'dialog_state': 'primary_assistant',
        'answer': 'My answer is blah blah blah'
    })
