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
    "name": "Test Conversation 2",
    "params": {"temperature": "0.395"},
}

response = requests.post(post_api_url, json=payload)

# Check if the request was successful
if response.status_code == 201:  # Assuming 201 Created is the success status
    print("Success:", response.json())
else:
    print("Error:", response.status_code)

'''
get the previous id from post, to test GET /conv.../{id}
'''
previous_json = response.json()
previous_id = previous_json.get("id", None)

get_api_url = f"http://localhost:8000/conversations/{id}"

full_url = get_api_url.format(id=previous_id)

response2 = requests.get(full_url)

# Check if the request was successful
if response2.status_code == 200:
    print("Success:", response2.json())
else:
    print("Error:", response2.status_code)

'''
Test posting a second conv
'''
payload2 = {
    "name": "Test Conversation 3",
    "params": {"temperature": "0.75"},
}

response3 = requests.post(post_api_url, json=payload2)
if response3.status_code == 201:  
    print("Success:", response3.json())
else:
    print("Error:", response3.status_code)

'''
  Test GET /conversations
'''
get_convs_api_url = f"http://localhost:8000/conversations"

get_convs_resp = requests.get(get_convs_api_url)
if get_convs_resp.status_code == 200:  
    print("Success:", get_convs_resp.json())
else:
    print("Error:", get_convs_resp.status_code)


'''
  Test PUT /conversations/{id}
'''
second_id_dict = response3.json()
second_id = second_id_dict.get("id", None)

put_api_url = f"http://localhost:8000/conversations/{id}"

full_put_url = put_api_url.format(id=second_id)

put_payload = {
    "name": "Tester",
    "params": {"temperature": "0.234"},
}

put_resp = requests.put(full_put_url, json=put_payload)
if put_resp.status_code == 204:  
    print("Success:", put_resp.json())
else:
    print("Error:", put_resp.status_code)