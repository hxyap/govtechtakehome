from fastapi import FastAPI, HTTPException, Path, Request
from typing import List
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from models import (
    Conversation,
    ConversationFull,
    ConversationPOST,
    Prompt,
    QueryRoleType,
    CreatedResponse,
    InternalServerError,
    NotFoundError,
    DeletedResponse,
    ConversationPUT,
    InvalidParametersError,
)
import os
from uuid import UUID, uuid4
import tiktoken
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
from collections import defaultdict

# initialize chatgpt client
load_dotenv(find_dotenv())

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details_dict = defaultdict(list)

    for e in exc.errors():
        loc_str = "->".join(str(part) for part in e["loc"])  # Convert location to string key
        error_details_dict[loc_str].append(e["msg"])

    error_message = InvalidParametersError(
        request={"path": str(request.url)},  # Example of including request details
        details=dict(error_details_dict)
    )
    return JSONResponse(
        status_code=400,
        content={"code": error_message.code, "errors": error_message.message}
    )

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
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
async def get_chatgpt_response(
    conversation_history: List[Prompt], query_message: Prompt, params
) -> str:
    # Convert conversation_history to the format expected by OpenAI
    conversation_history.append(query_message)
    temp = params.get("temperature", 0.35)

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=conversation_history,
            temperature=temp,
            # max_tokens=params.max_tokens
        )
        model_role = response.choices[0].message.role
        model_response = response.choices[0].message.content
        resp_as_prompt = Prompt(role=model_role, content=model_response)
    except Exception as e:
        raise InternalServerError()

    return resp_as_prompt


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/queries/{id}", response_model=CreatedResponse, status_code=201)
async def update_conversation_prompts(id: UUID, user_prompt: Prompt):
    """
    Adds the user prompt and gpt response to ConversationFull object
    """
    convo = await ConversationFull.find_one(ConversationFull.id == id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    old_tokens = convo.tokens
    prompt_tokens = len(encoding.encode(user_prompt.content))
    new_token_count = old_tokens + prompt_tokens
    # send message to chatgpt
    gpt_response = await get_chatgpt_response(
        conversation_history=convo.messages,
        query_message=user_prompt,
        params=convo.params,
    )
    # Append the new reply to the messages list

    # updated_messages = convo.messages.extend([user_prompt, gpt_response])    # Assuming user_prompt and gpt_response are objects you want to add to the conversation
    new_messages = convo.messages + [gpt_response]

    print(convo.messages)
    print(new_messages)
    # Save/update the conversation in the database
    # The specific method to do this will depend on your database library
    await convo.set(
        {
            ConversationFull.messages: new_messages,
            ConversationFull.tokens: new_token_count,
        }
    )

    return {"id": str(convo.id)}


@app.post(
    "/conversations",
    response_model=CreatedResponse,
    status_code=201,
    responses={
        500: {
            "model": InternalServerError,
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 500,
                        "message": "Internal server error occurred",
                    }
                }
            },
        },
        400: {
            "model": InvalidParametersError,
            "description": "Invalid Parameters Error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 400,
                        "message": "Parameters were invalid for the endpoint.",
                    }
                }
            },
        },
    },
)
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
        error_response = InternalServerError(code=500, message=str(e))
        return JSONResponse(status_code=500, content=error_response.dict())


@app.get("/conversations", response_model=List[ConversationFull], status_code=200)
async def update_conversation():
    """
    Takes in: probably user header through JWT or smth haha
    Returns: User's Conversation as a List
    """
    try:
        # Assuming you have a mechanism to authenticate and identify the user making the request
        # Replace `find_many` with the correct method based on your database driver or ORM
        conversations = await ConversationFull.find().to_list()
        if not conversations:
            return []  # Return an empty list if no conversations are found
        return conversations
    except Exception as e:
        # Log the exception details here if logging is set up
        return InternalServerError(details={e})


@app.put("/conversations/{id}", status_code=204)
async def update_conversation(id: UUID, convo_update: ConversationPUT):
    """
    Takes in: JSON Body formatted as a Conversation
    Returns: Convo UUID.
    """
    # Find the conversation by ID
    try:
        # Find the conversation by ID
        convo = await ConversationFull.find_one(Conversation.id == id)
        if not convo:
            raise NotFoundError(details={"error": "Conversation not found"})

        await convo.set(
            {
                ConversationFull.name: convo_update.name,
                ConversationFull.params: convo_update.params,
            }
        )

    except NotFoundError as e:
        # It's better to directly raise HTTPException for FastAPI to handle
        raise HTTPException(status_code=404, detail=str(e.details))
    except InternalServerError as e:
        # Log the exception details here, if logging is set up
        # It's not recommended to return the exception details directly to the client for security reasons
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/conversations/{id}", response_model=ConversationFull, status_code=200)
async def get_conversation(
    id: UUID = Path(..., description="The UUID of the conversation to retrieve")
):
    """
    Retrieves the Conversation History by ID
    """
    # Fetch conversation from database or storage
    try:
        convo = await ConversationFull.find(ConversationFull.id == id).first_or_none()
        if not convo:
            raise NotFoundError(details={e})
        return convo
    except NotFoundError as e:
        raise e
    except Exception as e:
        raise InternalServerError(details={e})

    # could not get this to work with DeletedResponse???


@app.delete("/conversations/{id}", status_code=204)
async def delete_conversation(
    id: UUID = Path(..., description="The UUID of the conversation to retrieve")
):
    """
    Deletes the specified conversation by ID.
    """
    # Fetch conversation from database or storage
    try:
        found_convo = await ConversationFull.find_one(ConversationFull.id == id)
        print(found_convo)
        if isinstance(found_convo, None):
            raise NotFoundError(details={e})
        await found_convo.delete()
    except NotFoundError as e:
        raise e
    except Exception as e:
        raise InternalServerError(details={e})


# do this later
# @app.post("/queries", response_model=Prompt)
# async def create_query(query: Prompt):
#     # Initialize or fetch the conversation
#     client_query =
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
