import requests
import re
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

def test_parse_html():
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&specials=1&infinite=1&cc=tr&l=english"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        html = data.get("results_html", "")
        
        # Regex patterns
        # Finding blocks might be safer, but let's try line-by-line or finding main anchors
        
        # Pattern to find each game row
        # <a href="..." data-ds-appid="123" ... > ... </a>
        
        # Let's find all appids first, then try to extract details for each block
        # Actually simplest is to iterate over "responsive_search_name_combined" blocks if possible,
        # but regex is linear.
        
        # Let's clean newlines for easier regex
        html_clean = html.replace("\n", "").replace("\r", "")
        
        # Regex to capture a game block
        # We look for <a ... data-ds-appid="(\d+)" ... class="search_result_row ..."> ... <span class="title">(.*?)</span> ... 
        
        # It's better to split by "search_result_row" or <a> tags?
        # <a href=... class="search_result_row ..."> matches the start.
        
        matches = re.finditer(r'<a href="[^"]+"[^>]+data-ds-appid="(\d+)"[^>]+class="search_result_row[^>]*>(.*?)</a>', html_clean, re.DOTALL)
        
        count = 0
        for match in matches:
            appid = match.group(1)
            content = match.group(2)
            
            # Extract name
            name_match = re.search(r'<span class="title">(.*?)</span>', content)
            name = name_match.group(1) if name_match else "Unknown"
            
            # Extract discount
            disc_match = re.search(r'discount_pct">-(\d+)%</div>', content)
            if disc_match:
                discount = int(disc_match.group(1))
            else:
                discount = 0
            
            # Extract prices (simple search)
            # <div class="discount_final_price">$4.64</div>
            # <div class="discount_original_price">$14.99</div>
            
            # Note: Prices might have currency symbols, commas etc.
            # We assume classes are present.
            
            if discount > 0:
                print(f"Found: {name} (ID: {appid}) - Discount: {discount}%")
                count += 1
                
        print(f"Total parsed with discount > 0: {count}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parse_html()
