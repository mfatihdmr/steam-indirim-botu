import requests
import re
import json
import os

# Steam için Tam Tarayıcı Başlıkları (Scraping/HTML için)
STEAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://store.steampowered.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

def get_search_discounts():
    """
    Steam Arama API'sini kullanarak 'Geniş Çaplı' indirim taraması yapar.
    Endpoint: /search/results/?query&start=0&count=50&specials=1&infinite=1
    """
    # Infinite scroll endpoint'i JSON döner (içinde HTML vardır)
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&specials=1&infinite=1&cc=tr&l=english"
    
    print(f"URL taranıyor: {url}")
    
    try:
        # Steam isteğine de browser başlıklarını ekle
        response = requests.get(url, headers=STEAM_HEADERS, timeout=10)
        print(f"Response Code: {response.status_code}")
        
        data = response.json()
        
        if "results_html" not in data:
            print("API yanıtında 'results_html' bulunamadı.")
            print(f"Response Keys: {data.keys()}")
            return []
            
        html = data["results_html"].replace("\n", "").replace("\r", "")
        print(f"HTML Content Length: {len(html)}")
        
        # Regex ile oyun kutularını bul
        matches = re.finditer(r'<a href="[^"]+"[^>]+data-ds-appid="(\d+)"[^>]+class="search_result_row[^>]*>(.*?)</a>', html, re.DOTALL)
        
        candidates = []
        
        for match in matches:
            appid = match.group(1)
            content = match.group(2)
            
            # İsim
            name_match = re.search(r'<span class="title">(.*?)</span>', content)
            name = name_match.group(1) if name_match else "Unknown"
            
            # İndirim Oranı
            disc_match = re.search(r'discount_pct">-(\d+)%</div>', content)
            discount = int(disc_match.group(1)) if disc_match else 0
            
            # Fiyatlar
            final_match = re.search(r'discount_final_price">([^<]+)</div>', content)
            final_price = final_match.group(1) if final_match else "?"
            
            orig_match = re.search(r'discount_original_price">([^<]+)</div>', content)
            orig_price = orig_match.group(1) if orig_match else "?"
            
            if discount > 0 and appid != "3949040":
                candidates.append({
                    "appid": int(appid),
                    "name": name,
                    "discount": discount,
                    "final": final_price,
                    "orig": orig_price
                })
                
        return candidates

    except Exception as e:
        print(f"Arama API taraması sırasında hata: {e}")
        return []


def main():
    # Windows konsolunda Unicode karakterleri yazdırmak için
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("İndirimler kontrol ediliyor (REPRO)...")
    
    candidates = get_search_discounts()
    
    print(f"Bulunan toplam potansiyel fırsat sayısı: {len(candidates)}")
    
    # Load sent.json
    sent = []
    if os.path.exists("sent.json"):
        with open("sent.json", "r", encoding="utf-8") as f:
            sent = json.load(f)
            
    print(f"Daha önce gönderilen oyun sayısı: {len(sent)}")

    new_count = 0
    for c in candidates:
        if c['appid'] not in sent:
            print(f" [YENİ] {c['name']} (%{c['discount']})")
            new_count += 1
        else:
            # print(f" [ESKİ] {c['name']} (%{c['discount']})")
            pass
            
    print(f"\nToplam yeni fırsat: {new_count}")

if __name__ == "__main__":
    main()
