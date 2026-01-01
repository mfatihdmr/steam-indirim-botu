import requests

url = "https://cdn.akamai.steamstatic.com/steam/apps/3405690/header.jpg"
try:
    print(f"Checking URL: {url}")
    response = requests.head(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code != 200:
        print("HEAD request failed, trying GET...")
        response = requests.get(url, stream=True, timeout=5)
        print(f"GET Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
except Exception as e:
    print(f"Error: {e}")
