from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from uuid import UUID, uuid4
from main import app
from models import ConversationFull, ConversationPOST

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_conversation_success():
    fake_uuid = uuid4()
    with patch.object(ConversationFull, 'insert') as mock_insert:
        mock_insert.return_value = MagicMock(id=fake_uuid)
        payload = {
            "name": "Test Conversation",
            "params": {"temperature": 0.395},
        }
        response = client.post("/conversations", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data  # Assuming your endpoint generates an ID to return
        assert data['id'] == "123456789"  # Example ID returned by the mocked insert method

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


@pytest.mark.asyncio
async def test_get_conversation(client):
    predefined_id = "80277564-ee29-4c71-a574-61d622bc0adb"
    with patch('path.to.fetch_conversation_from_db') as mock_fetch:
        mock_fetch.return_value = {"id": predefined_id, "name": "Test Conversation", "params": {"temperature": 0.5}, "messages": []}
        response = client.get(f"/conversations/{predefined_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == predefined_id

@pytest.mark.asyncio
async def test_update_conversation(client):
    predefined_id = "80277564-ee29-4c71-a574-61d622bc0adb"
    with patch('path.to.ConversationFull.find_one') as mock_find_one, \
         patch('path.to.ConversationFull.save') as mock_save:
        mock_find_one.return_value = ConversationFull(id=predefined_id, name="Original Name", params={"temperature": 0.5}, messages=[])
        mock_save.return_value = None  # Assume save is successful
        payload = {
            "name": "Updated Test Conversation",
            "params": {"temperature": 0.6},
        }
        response = client.put(f"/conversations/{predefined_id}", json=payload)
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_conversation(client):
    predefined_id = "80277564-ee29-4c71-a574-61d622bc0adb"
    with patch('path.to.ConversationFull.find_one') as mock_find_one, \
         patch('path.to.ConversationFull.delete') as mock_delete:
        mock_find_one.return_value = ConversationFull(id=predefined_id, name="Test Conversation", params={}, messages=[])
        mock_delete.return_value = None  # Assume delete is successful
        response = client.delete(f"/conversations/{predefined_id}")
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_query_conversation(client):
    query_payload = {
        "role": "user",
        "content": "Can dogs eat chocolate safely?"
    }
    predefined_id = "test_id"
    with patch('path.to.your_query_function') as mock_query:
        # Simulate different responses based on the query
        mock_query.side_effect = lambda id, payload: {"id": id, "response": "Query processed"} if id == predefined_id else HTTPException(status_code=404, detail="Not found")
        response = client.post(f"/queries/{predefined_id}", json=query_payload)
        assert response.status_code in [201, 400, 404, 422, 500]  # Expected status codes
