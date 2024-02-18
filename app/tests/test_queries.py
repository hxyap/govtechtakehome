from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import os
from uuid import UUID, uuid4
from main import app
from models import ConversationFull, ConversationPOST, ConversationPUT, Prompt
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from httpx import AsyncClient
from openai import AsyncOpenAI

# Initialize the client for mocking purposes
client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
test_client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
async def mock_db():
    mock_client = AsyncMongoMockClient("mongodb://localhost:27017")
    db = mock_client["govtech_backend"]
    await init_beanie(document_models=[ConversationFull], database=db)
    yield db

@pytest.mark.asyncio
async def test_update_conversation_prompts_not_found():
    test_uuid = uuid4()
    user_prompt = Prompt(role="user", content="Test prompt")  
    with patch.object(ConversationFull, 'get', return_value=None):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/queries/{test_uuid}", json=user_prompt.dict())
            assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_conversation_prompts_internal_error():
    test_uuid = uuid4()
    user_prompt = Prompt(role="user", content="Test prompt")
    with patch.object(ConversationFull, 'get', side_effect=Exception("Database error")):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/queries/{test_uuid}", json=user_prompt.dict())
            assert response.status_code == 500

@pytest.mark.asyncio
async def test_query_invalid_params():
    test_uuid = ()
    user_prompt = Prompt(role="user", content="Test prompt") 
    with patch('models.ConversationFull.get', return_value=None):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/queries/{test_uuid}", json=user_prompt.dict())
            assert response.status_code == 400

### WILL BE FIXING THIS BY CHECKING HOW TO IMPORT OPENAI LIBRARY
# @pytest.mark.asyncio
# async def test_update_conversation_prompts_chatgpt_422_error():
#     test_uuid = uuid4()
#     user_prompt = {"role": "user", "content": "Test prompt"}  # Adjust based on your model

#     # Mock the AsyncOpenAI client's method
#     with patch('app.main.client.chat.completions.create', new_callable=AsyncMock) as mock_create:
#         mock_create.side_effect = HTTPException(status_code=422, detail="Unable to create resource.")

#         async with AsyncClient(app=app, base_url="http://test") as ac:
#             response = await ac.post(f"/queries/{test_uuid}", json=user_prompt)
#             assert response.status_code == 422