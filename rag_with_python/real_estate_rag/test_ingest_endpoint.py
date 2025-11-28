"""
Test the /ingest endpoint and show detailed error
"""
import requests

url = "http://localhost:8000/ingest"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    try:
        print(f"Response JSON: {response.json()}")
    except:
        pass
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Text: {e.response.text}")
