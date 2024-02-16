from fastapi.testclient import TestClient
from app import main  # Import your FastAPI app here

client = TestClient(main)

def test_create_conversation():
    # Define the endpoint
    url = "/conversations"
    
    # Define the request body
    data = {
        "name": "Test Conversation",
        "params": {
            "temperature": 0.3,
        }
    }
    
    # Make a POST request to the endpoint
    response = client.post(url, json=data)
    
    # Assert the status code for a successful creation
    assert response.status_code == 201
    
    # Optionally, check the response body
    response_data = response.json()
    assert "id" in response_data  # Example assertion