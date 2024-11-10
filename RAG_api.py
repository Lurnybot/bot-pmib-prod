
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory import ChatMessageHistory
from langchain.chains import LLMChain


from langchain.vectorstores import FAISS
import faiss
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from uuid import uuid4
from langchain_core.output_parsers import StrOutputParser
import asyncio
import time
from datetime import date
from datetime import datetime
from configparser import ConfigParser
import json
from prompt_templates import system_prompt,follow_up_prompt,language_detection_prompt
from utilities import get_context, get_context_scraped

import os


# Read config file
config = ConfigParser()
config.read('./app.cfg')

api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI( 
    docs_url=None,           # Disable Swagger UI at /docs
    redoc_url=None,          # Disable ReDoc UI at /redoc
                )


ALLOWED_ORIGINS = json.loads(config.get('middleware', 'allowed_origins'))
CLIENT_DOMAIN  = config.get('client_id', 'client_domain')
REFERER_DOMAIN = json.loads(config.get('middleware', 'refer_domain'))

EMBEDDING_MODEL = config.get('model_config', 'embedding_model')
GPT_MODEL = config.get('model_config', 'llm_model')
TEMPERATURE = config.getfloat('model_config', 'temperature')
MAX_TOKENS = config.getint('model_config', 'max_tokens')

KB = config.get('knowledge_base', 'storage_path') + config.get('knowledge_base', 'filename')  
KB_SCORE_THRESHOLD = config.getfloat('knowledge_base', 'kb_score_threshold')
KB_TOP_K = config.getint('knowledge_base', 'top_k')
kb_params=  {"score_threshold":KB_SCORE_THRESHOLD, 'k': KB_TOP_K}
print("KB path: >>>>", KB)

#***************************     Model Intialization    **************************************************************

embeddings = OpenAIEmbeddings(model = EMBEDDING_MODEL)
llm = ChatOpenAI(api_key= api_key, model=GPT_MODEL, max_tokens=MAX_TOKENS, streaming=True, temperature= TEMPERATURE)

loaded_vector_store = FAISS.load_local(KB, embeddings, allow_dangerous_deserialization=True)
retriever = loaded_vector_store.as_retriever()

#********************************************************************************************************************

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] ,  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# # Middleware to add X-Frame-Options and Content-Security-Policy
# class SecurityHeadersMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         response = await call_next(request)
#         response.headers['X-Frame-Options'] = 'ALLOW-FROM {}'.format(CLIENT_DOMAIN)  # Replace with the client domain
#         response.headers['Content-Security-Policy'] = "frame-ancestors 'self' {}".format(CLIENT_DOMAIN)
#         return response

# app.add_middleware(SecurityHeadersMiddleware)


# @app.middleware("http")
# async def check_referer(request: Request, call_next):
#     referer = request.headers.get("referer")
#     print(">>>>>>===>>>>> Referer: ", referer)
#     allowed_domains = REFERER_DOMAIN
#     print("Allowed Referers: ", allowed_domains)
    
#     if referer and not any(domain in referer for domain in allowed_domains):
#         return HTMLResponse(content="<h1>Access Forbidden</h1><p>You are not authorized to access this resource.</p>", status_code=403)
    
#     response = await call_next(request)
#     return response


# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     if exc.status_code == 403:
#         return HTMLResponse(content="<h1>Access Forbidden</h1><p>You are not authorized to view this page.</p>", status_code=403)
#     return HTMLResponse(content="<h1>Error</h1><p>Something went wrong.</p>", status_code=500)




res_prompt=  PromptTemplate(template= system_prompt, input_variables= ['question, context','language_detected'])

follow_up_prompt_template=  PromptTemplate(template= follow_up_prompt, input_variables= ['history, question'])

language_detection_prompt_template = PromptTemplate(template=language_detection_prompt,input_variables=['question'])

parser = StrOutputParser()


async def generate_stream(chain, user_query, context, final_response,language_detected):
    # Create a chat completion request
    # Yield the streaming response

    stream = chain.astream({"question": user_query, "context": context, "date": str(time.ctime()),"language_detected":language_detected})
    async for chunk in stream:
        # print(chunk, type(chunk))  # Iterate over the streaming generator asynchronously
        # print(chunk, end="|", flush=True)  # Stream the output (you can modify the separator if needed)
        final_response += chunk  # Append each chunk content to the final response
        yield chunk

        # Once the streaming is done, save the final response to a file
    
    print(final_response)



sessions = {}


def create_session(session_id, sessions):
    if session_id not in sessions.keys():
        sessions[session_id] = {
            "history": [],
            "created_timestamp": datetime.now()  # Store the current timestamp
        }
        print("Session Created")
    else:
        print("Session Already exists for {}".format(session_id))



def check_expired_sessions(sessions, expiry_minutes=60):
    current_time = datetime.now()
    expired_sessions = []

    for session_id, session_info in list(sessions.items()):  # Use list() to avoid runtime error
        if (current_time - session_info["created_timestamp"]).total_seconds() / 60 > expiry_minutes:
            print(f"Session {session_id} has expired.")
            expired_sessions.append(session_id)

    for session_id in expired_sessions:
        del sessions[session_id]


# Background task to clean up expired sessions
async def cleanup_sessions():
    while True:
        check_expired_sessions(sessions)
        await asyncio.sleep(3600)  # Run every hour or any desired interval




@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_sessions())



@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_query = data.get("query", "")
    session_id = data.get("sessionId", "")

    # detected_language = detect(data.get("query", ""))

    print(data)
    
    # Ensure the user_query is not empty
    if not user_query:
        return {"error": "No query provided"}
    

    
    ## Create new session if user doesnt exists
    create_session(session_id= session_id, sessions= sessions )
    print("All Sessions in memory: ", sessions.keys())


    lang_detect_chain = language_detection_prompt_template | llm | parser

    # user_query = "Hello How are you"

    language_detected = lang_detect_chain.invoke({"question":user_query})
    
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Language>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n", language_detected)


    ## Create follow up standalone query
    follow_chain = follow_up_prompt_template | llm | parser
    
    history_str = "\nUser:".join(sessions[session_id]["history"])
    print(history_str)
    # history_str = ''
    
    new_query = follow_chain.invoke({"history": history_str, "question": user_query})
    print("New Query: >>>>", new_query)
    
    ### Add new query to message hgistory    
    sessions[session_id]['history'].append(new_query)
    #### Keeping only last 4 messages of the session history
    sessions[session_id]['history'] = sessions[session_id]['history'][-10:]
    print("session_id : {}\n\n History: {}".format(session_id, sessions[session_id]))



    chain = res_prompt | llm | parser
    context = get_context_scraped(query=new_query, retriever=retriever,config=kb_params)
    final_response=  ""
    return StreamingResponse(generate_stream(chain, new_query, context, final_response,language_detected), media_type="text/plain")


# 1. Serve static files (Chatbot UI)
app.mount("/", StaticFiles(directory="out", html=True), name="static")



if __name__ == "__main__":
    uvicorn.run("RAG_api:app", host="localhost", port=8000, reload=False)



