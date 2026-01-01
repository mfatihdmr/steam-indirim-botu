import requests
import json
import os

def get_steam_all_categories():
    url = "https://store.steampowered.com/api/featuredcategories?cc=tr&l=english"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        print("Keys in response:", data.keys())
        
        all_candidates = []
        
        # Categories to check
        categories = ["specials", "top_sellers", "new_releases", "daily_deal", "coming_soon"]
        
        for cat in categories:
            if cat in data and "items" in data[cat]:
                items = data[cat]["items"]
                print(f"Category '{cat}' has {len(items)} items.")
                
                for item in items:
                    # Check for discount
                    discount = item.get("discount_percent", 0)
                    if discount >= 20: # Same filter as original
                        all_candidates.append({
                            "appid": item["id"],
                            "name": item["name"],
                            "discount": discount,
                            "source": cat
                        })
            else:
                print(f"Category '{cat}' not found or empty.")
                
        return all_candidates
    except Exception as e:
        print(f"API Error: {e}")
        return []

def main():
    print("--- DEBUG EXPANDED START ---")
    
    # Load sent to see overlap
    sent = []
    if os.path.exists("sent.json"):
        with open("sent.json", "r") as f:
            sent = json.load(f)
            
    print(f"Sent count: {len(sent)}")
    
    candidates = get_steam_all_categories()
    print(f"Total candidates found across all categories: {len(candidates)}")
    
    # Dedup by appid
    unique_candidates = {c["appid"]: c for c in candidates}.values()
    print(f"Unique candidates: {len(unique_candidates)}")
    
    new_candidates = [c for c in unique_candidates if c["appid"] not in sent]
    print(f"New candidates (not in sent.json): {len(new_candidates)}")
    
    for c in new_candidates:
        print(f" [NEW] {c['name']} (-{c['discount']}%) from {c['source']}")

    print("--- DEBUG EXPANDED END ---")

if __name__ == "__main__":
    main()
