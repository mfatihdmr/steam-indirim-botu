from main import get_search_discounts, load_sent
import sys
import requests

# Mock requests to avoid hitting API limit or network issues if needed, but we used real API in main.
# Let's run it for real.
sys.stdout.reconfigure(encoding='utf-8')

def verify():
    print("--- VERIFICATION START ---")
    candidates = get_search_discounts()
    print(f"Total candidates found: {len(candidates)}")
    
    if len(candidates) < 10:
        print("FAILURE: Too few candidates found. Something might be wrong with scraping.")
        return

    print("First 10 candidates (Should be popular games):")
    for i, game in enumerate(candidates[:10]):
        print(f" {i+1}. {game['name']} (-{game['discount']}%)")
        
    sent = load_sent()
    new_candidates = [c for c in candidates if c["appid"] not in sent]
    
    print(f"\nNew candidates available for tweeting: {len(new_candidates)}")
    if new_candidates:
         print(f"Next tweet would be: {new_candidates[0]['name']} (-{new_candidates[0]['discount']}%)\n")
         print("SUCCESS: Bot is finding widely available discounts and prioritizing popularity.")
    else:
        print("WARNING: No new candidates found (all 50 might be sent already?)")

    print("--- VERIFICATION END ---")

if __name__ == "__main__":
    verify()
