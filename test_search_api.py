import requests
import json
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

def test_search_api():
    # Attempt to hit the search results endpoint expecting JSON (infinite=1)
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&specials=1&infinite=1&cc=tr&l=english"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("Response is valid JSON.")
            print("Keys:", data.keys())
            
            if "results_html" in data:
                print(f"Contains 'results_html' of length: {len(data['results_html'])}")
                print("First 500 chars of HTML:")
                print(data['results_html'][:500])
            
            if "total_count" in data:
                print(f"Total results available: {data['total_count']}")
                
        except json.JSONDecodeError:
            print("Response is NOT JSON.")
            print(response.text[:500])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search_api()
