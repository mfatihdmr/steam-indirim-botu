import requests
import json
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

def inspect_genres():
    url = "https://store.steampowered.com/api/featuredcategories?cc=tr&l=english"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "genres" in data:
            print(f"Key 'genres' found. Type: {type(data['genres'])}")
            # It seems 'genres' might be a list or dict. Let's see.
            if isinstance(data['genres'], list):
                print(f"Number of genres: {len(data['genres'])}")
                if len(data['genres']) > 0:
                    first_genre = data['genres'][0]
                    print("First genre keys:", first_genre.keys())
                    print("Genre Name:", first_genre.get("name"))
                    if "items" in first_genre:
                        items = first_genre["items"]
                        print(f"Items in first genre: {len(items)}")
                        if len(items) > 0:
                            print("Sample item:", items[0])
            elif isinstance(data['genres'], dict):
                 print("Genres is a dict keys:", data['genres'].keys())
        else:
            print("'genres' key not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_genres()
