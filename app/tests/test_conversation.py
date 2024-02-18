from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from uuid import UUID, uuid4
from main import app
from models import ConversationFull, ConversationPOST, ConversationPUT
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from httpx import AsyncClient

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
async def mock_db():
    mock_client = AsyncMongoMockClient("mongodb://localhost:27017")
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
async def test_get_conversation_internal_server_error():
    test_uuid = uuid4()
    with patch.object(ConversationFull, 'get', side_effect=Exception("Database error")):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/conversations/{test_uuid}")
            assert response.status_code == 500
            data = response.json()
            assert data['code'] == 500
            # assert "Internal server error" in data['message']


@pytest.mark.asyncio
async def test_get_conversation_not_found():
    # Generate a random UUID
    test_uuid = uuid4()
    # Patch the ConversationFull.get method to return None
    with patch('models.ConversationFull.get', return_value=None):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/conversations/{test_uuid}")
            assert response.status_code == 404




@pytest.mark.asyncio
async def test_get_conversation_invalid_params():
    test_uuid = ()
    with patch('models.ConversationFull.get', return_value=None):
        response = client.get(f"/conversations/{test_uuid}")
        assert response.status_code == 400
        # data = response.json()
        # assert data['detail'] == "Conversation not found"



@pytest.mark.asyncio
async def test_get_conversation_internal_server_error2():
    test_uuid = uuid4()
    with patch('models.ConversationFull.get', side_effect=Exception("Unexpected error")):
        response = client.get(f"/conversations/{test_uuid}")
        assert response.status_code == 500
        # data = response.json()
        # assert data['code'] == 500

@pytest.mark.asyncio
async def test_delete_conversation_not_found():
    with patch('models.ConversationFull.get', new_callable=AsyncMock, return_value=None) as mock_get:
        test_id = str(uuid4())
        response = client.delete(f"/conversations/{test_id}")
        mock_get.assert_awaited_once()
        assert response.status_code == 404
        data = response.json()
        assert data['code'] == 404

@pytest.mark.asyncio
async def test_delete_conversation_internal_server_error():
    with patch('models.ConversationFull.get', side_effect=Exception("Internal server error")):
        test_id = str(uuid4())
        response = client.delete(f"/conversations/{test_id}")
        assert response.status_code == 500
        data = response.json()
        assert data['code'] == 500
        assert "Internal server error" in data['message']

@pytest.mark.asyncio
async def test_get_all_conversations_internal_server_error():
    # Mock the find().to_list() method chain to raise an exception
    with patch.object(ConversationFull, 'find', side_effect=Exception("Database error")) as mock_find:
        client = TestClient(app)
        response = client.get("/conversations")  # Adjust the URL to match your endpoint
        assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_conversation_invalid_request():
    invalid_uuid = "not-a-uuid"
    convo_update = {"name": "Updated Name", "params": {"param": "value"}}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/conversations/{invalid_uuid}", json=convo_update)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_conversation_internal_server_error():
    test_uuid = uuid4()
    convo_update = ConversationPUT(name="Updated Name", params={"param": "value"})  # Adjust based on your model
    with patch('models.ConversationFull.get', return_value=MagicMock()) as mock_get:
        mock_get.return_value.set.side_effect = Exception("Database error")
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/conversations/{test_uuid}", json=convo_update.dict())
            assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_conversation_not_found():
    test_uuid = uuid4()
    convo_update = ConversationPUT(name="Updated Name", params={"param": "value"})  # Adjust based on your model
    with patch('models.ConversationFull.get', return_value=None):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/conversations/{test_uuid}", json=convo_update.dict())
            assert response.status_code == 404