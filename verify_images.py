from main import get_search_discounts, load_sent
import sys
import requests
import os

sys.stdout.reconfigure(encoding='utf-8')

def verify_image():
    print("--- IMAGE VERIFICATION START ---")
    candidates = get_search_discounts()
    print(f"Total candidates found: {len(candidates)}")
    
    # Let's test image download for the first 5 candidates
    for i, game in enumerate(candidates[:5]):
        print(f"\nEvaluating Game: {game['name']} (ID: {game['appid']})")
        print(f"Primary Image: {game['header_image']}")
        print(f"Fallback Image: {game['fallback_image']}")
        
        success = False
        
        # Test Primary
        try:
            r = requests.head(game['header_image'], timeout=5)
            if r.status_code == 200:
                print("PRIMARY IMAGE OK (200)")
                success = True
            else:
                 print(f"PRIMARY IMAGE FAILED ({r.status_code})")
        except Exception as e:
            print(f"PRIMARY ERROR: {e}")
            
        # Test Fallback if primary failed
        if not success and game['fallback_image']:
             try:
                r = requests.head(game['fallback_image'], timeout=5)
                if r.status_code == 200:
                    print("FALLBACK IMAGE OK (200)")
                    success = True
                else:
                     print(f"FALLBACK IMAGE FAILED ({r.status_code})")
             except Exception as e:
                print(f"FALLBACK ERROR: {e}")
        
        if success:
            print(">>> Image Check: PASS")
        else:
            print(">>> Image Check: FAIL")

    print("\n--- IMAGE VERIFICATION END ---")

if __name__ == "__main__":
    verify_image()
