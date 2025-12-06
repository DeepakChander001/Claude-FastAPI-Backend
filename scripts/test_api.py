import httpx
import json

def test_generate():
    url = "http://127.0.0.1:8000/api/generate"
    
    # 1. Valid Request
    payload = {
        "prompt": "Hello, Claude!",
        "model": "claude-3.5",
        "max_tokens": 100
    }
    
    print(f"Sending valid request to {url}...")
    try:
        response = httpx.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "-"*30 + "\n")

    # 2. Invalid Request (Missing prompt)
    invalid_payload = {
        "model": "claude-3.5"
    }
    print(f"Sending INVALID request (missing prompt) to {url}...")
    try:
        response = httpx.post(url, json=invalid_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate()
