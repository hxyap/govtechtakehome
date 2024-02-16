from fastapi import FastAPI, APIRouter, HTTPException
from typing import List
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from models import Conversation, ConversationFull, ConversationPOST, Prompt, QueryRoleType, CreatedResponse, InternalServerError  # Adjust the import path as needed
import os
import json
import tiktoken
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
# initialize chatgpt client
load_dotenv(find_dotenv())

app = FastAPI()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# count number of tokens used by conversation
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


async def init_database():
    db_client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
    db = db_client["govtech_backend"]
    await init_beanie(database=db, document_models=[ConversationFull])

# Add a startup event handler to call init_database when the app starts
@app.on_event("startup")
async def startup_event():
    await init_database()

# Your endpoint definitions using Prompt and QueryRoleType
async def get_chatgpt_response(conversation_history: List[Prompt], query_message: str, params) -> str:
    # Convert conversation_history to the format expected by OpenAI
    messages_formatted = [{"role": msg.role, "content": msg.content} for msg in conversation_history]
    messages_formatted.append({"role": "user", "content": query_message})

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages_formatted,
            temperature=params.temperature,
            max_tokens=params.max_tokens
        )
        model_response = response.choices[0].message['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {str(e)}")

    return model_response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/conversations", response_model=CreatedResponse, status_code=201)
async def create_conversation(convo: ConversationPOST):
    """
      Takes in: JSON Body formatted as a Conversation
      Returns: Convo UUID.
    """
    try:
        convo_full = ConversationFull(**convo.dict(), messages=[])
        res = await convo_full.insert()
        print(res)
        return {"id": str(convo_full.id)} 
    except Exception as e:
        return InternalServerError(details={e})

#do this later
# @app.post("/queries", response_model=Prompt)
# async def create_query(query: Prompt):
#     # Initialize or fetch the conversation
#     client_query = 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)