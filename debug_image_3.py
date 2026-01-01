import requests

# Try the capsule image
url = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3405690/capsule_616x353.jpg"
try:
    print(f"Checking URL: {url}")
    response = requests.head(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print("HEAD failed, testing GET...")
        response = requests.get(url, stream=True, timeout=5)
        print(f"GET Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
