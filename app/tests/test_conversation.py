from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from uuid import UUID, uuid4
from main import app
from models import ConversationFull, ConversationPOST
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie

client = TestClient(app)

@pytest.fixture(autouse=True)
async def mock_db():
    mock_client = AsyncMongoMockClient()
    db = mock_client["govtech_backend"]
    await init_beanie(document_models=[ConversationFull], database=db)
    yield db

# @pytest.mark.asyncio
# async def test_create_conversation_success(mock_db):
#     async with mock_db as db:
#         payload = {
#             "name": "Mocked Conversation",
#             "params": {"temperature": 0.5},
#             "messages": []
#         }

#         # Perform the POST request to create a new conversation
#         response = client.post("/conversations", json=payload)

#         # Validate the response
#         assert response.status_code == 201
#         data = response.json()
#         assert 'id' in data


@pytest.mark.asyncio
async def test_create_conversation_internal_server_error():
    with patch.object(ConversationFull, 'insert', side_effect=Exception("Database error")):
        payload = {
            "name": "Test Conversation",
            "params": {"temperature": 0.395},
        }
        response = client.post("/conversations", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert data['code'] == 500
        # assert data['message'] == "Internal server error occurred"

@pytest.mark.asyncio
async def test_create_conversation_invalid_parameters():
    payload = {}  # Invalid payload missing required fields
    response = client.post("/conversations", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 400
    # assert "Parameters were invalid for the endpoint." in data['message']


# @pytest.mark.asyncio
# async def test_get_conversation_success():
#     test_uuid = uuid4()
#     test_conversation = ConversationFull(id=test_uuid, name="Test Conversation", params={"temperature": 0.5}, messages=[])
#     with patch('models.ConversationFull.get', return_value=test_conversation):
#         response = client.get(f"/conversations/{test_uuid}")
#         assert response.status_code == 200
#         data = response.json()
#         assert data['id'] == str(test_uuid)
#         assert data['name'] == "Test Conversation"




@pytest.mark.asyncio
async def test_get_conversation_invalid_params():
    test_uuid = ()
    with patch('models.ConversationFull.get', return_value=None):
        response = client.get(f"/conversations/{test_uuid}")
        assert response.status_code == 400
        # data = response.json()
        # assert data['detail'] == "Conversation not found"



@pytest.mark.asyncio
async def test_get_conversation_internal_server_error():
    test_uuid = uuid4()
    with patch('models.ConversationFull.get', side_effect=Exception("Unexpected error")):
        response = client.get(f"/conversations/{test_uuid}")
        assert response.status_code == 500
        # data = response.json()
        # assert data['code'] == 500



