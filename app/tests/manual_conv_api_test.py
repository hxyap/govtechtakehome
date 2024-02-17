'''
Ideally use mocks but I got tired of using Postman. So I'm using requests to automate testing instead.
'''
import requests

'''
Test posting convs
'''
post_api_url = "http://localhost:8000/conversations"

# Example payload
payload = {
    "name": "Test Convo 2",
    "params": {"temperature": 0.395},
}

response = requests.post(post_api_url, json=payload)

# Check if the request was successful
if response.status_code == 201:  # Assuming 201 Created is the success status
    print("Success - POST'd first Conversation:", response.json())
else:
    print("Error:", response.status_code)

'''
get the previous id from post, to test GET /conv.../{id}
'''
previous_json = response.json()
previous_id = previous_json.get("id", None)

get_api_url = f"http://localhost:8000/conversations/{previous_id}"
response2 = requests.get(get_api_url)

# Check if the request was successful
if response2.status_code == 200:
    print("Success - Retrieved first Conversation:", response2.json())
else:
    print("Error:", response2.status_code)

'''
Test posting a second conv
'''
payload2 = {
    "name": "Test Convo 3",
    "params": {"temperature": 0.75},
}

response3 = requests.post(post_api_url, json=payload2)
if response3.status_code == 201:  
    print("Success - POST'd second convo:", response3.json())
else:
    print("Error:", response3.status_code)

'''
  Test GET /conversations
'''
get_convs_api_url = f"http://localhost:8000/conversations"

get_convs_resp = requests.get(get_convs_api_url)
if get_convs_resp.status_code == 200:  
    print("Success - Retrieved all convos:", get_convs_resp.json())
else:
    print("Error:", get_convs_resp.status_code)


'''
  Test PUT /conversations/{id}
'''
second_id_dict = response3.json()
second_id = second_id_dict.get("id", None)

put_api_url = f"http://localhost:8000/conversations/{second_id}"

put_payload = {
    "name": "Tester",
    "params": {"temperature": 0.234}
}

put_resp = requests.put(put_api_url, json=put_payload)
if put_resp.status_code == 204:  
    print("Success - PUT request worked on 2nd: No content")
else:
    print("Error:", put_resp.status_code)


'''
    Test delete on second id.
'''
delete_api_url = f"http://localhost:8000/conversations/{second_id}"

# Send DELETE request
delete_response = requests.delete(delete_api_url)

# Check if the request was successful
if delete_response.status_code == 204:
    print(f"Success: Conversation with ID {second_id} deleted.")
else:
    print(f"Error: {delete_response.status_code}, could not delete conversation.")

'''
  Check if the id is deleted - 
'''
get_convs_api_url = f"http://localhost:8000/conversations"

get_convs_resp = requests.get(get_convs_api_url)
if get_convs_resp.status_code == 200:  
    print("Success:", get_convs_resp.json())
else:
    print("Error:", get_convs_resp.status_code)

'''
    Test queries endpt for first id.
'''

queries_api_url = f"http://localhost:8000/queries/{previous_id}"

# Example payload for the POST request to /queries/{id}
# Adjust this payload based on what your /queries/{id} endpoint expects
query_payload = {
    "role": "user",
    "content": "Can dogs eat chocolate safely?"
}

# Send POST request
queries_response = requests.post(queries_api_url, json=query_payload)

# Check if the request was successful
if queries_response.status_code == 201:
    queries_response_json = queries_response.json()
    print("Success:", queries_response_json)

    # Further validation to check if the "id" in response is as expected
    if "id" in queries_response_json and queries_response_json["id"] == previous_id:
        print(f"Received expected ID: {queries_response_json['id']}")
    else:
        print("Unexpected response body.")
else:
    print(f"Error: {queries_response.status_code}")

'''
  One more check to see if the tokens have been updated as well as whether the convo has been updated.
'''
get_convs_api_url = f"http://localhost:8000/conversations"

get_convs_resp = requests.get(get_convs_api_url)
if get_convs_resp.status_code == 200:  
    print("Success:", get_convs_resp.json())
else:
    print("Error:", get_convs_resp.status_code)

'''
    Test queries endpt for first id.
'''

queries_api_url = f"http://localhost:8000/queries/{previous_id}"
