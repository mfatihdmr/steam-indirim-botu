import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import tweepy

# ⚠️ GÜVENLİK UYARISI:
# API anahtarlarını ASLA buraya doğrudan yazmayın!
# GitHub'a yüklendiği an anahtarlarınız iptal edilir.
# Bu anahtarları GitHub Repository Settings -> Secrets -> Actions kısmına eklemelisiniz.

# X API Kimlik Bilgileri (GitHub Secrets'tan otomatik okunur)
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

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

# Twitter için Temiz Başlıklar (API JSON için)
# Sadece User-Agent'ı değiştiriyoruz, 'python-requests' yerine tarayıcı gibi gözüksün ama API yapısını bozmasın.
TWITTER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# X API v2 Client (Global Olarak Tanımla)
client = None
if all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    # Twitter oturumuna özel başlığı ekle (Diğerlerini karıştırma)
    client.session.headers.update(TWITTER_HEADERS)

def load_sent():
    """Daha önce gönderilen oyunların listesini yükler."""
    if not os.path.exists("sent.json"):
        return []
    try:
        with open("sent.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("sent.json okunamadı (bozuk veya yanlış kodlama), boş liste ile devam ediliyor.")
        return []


def save_sent(lst):
    """Gönderilen oyunların listesini kaydeder."""
    with open("sent.json", "w", encoding="utf-8") as f:
        json.dump(lst, f)


import re

def get_search_discounts():
    """
    Steam Arama API'sini kullanarak 'Geniş Çaplı' indirim taraması yapar.
    Endpoint: /search/results/?query&start=0&count=50&specials=1&infinite=1
    Bu yöntem 30-50+ arası indirimli oyunu 'Alaka Düzeyi' (Popülerlik) sırasına göre verir.
    """
    # Infinite scroll endpoint'i JSON döner (içinde HTML vardır)
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&specials=1&infinite=1&cc=tr&l=english"
    
    try:
        # Steam isteğine de browser başlıklarını ekle
        response = requests.get(url, headers=STEAM_HEADERS, timeout=10)
        data = response.json()
        
        if "results_html" not in data:
            print("API yanıtında 'results_html' bulunamadı.")
            return []
            
        html = data["results_html"].replace("\n", "").replace("\r", "")
        
        # Regex ile oyun kutularını bul
        # Her bir oyun <a> etiketi içindedir ve data-ds-appid özniteliği taşır
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
            
            # Fiyatlar (Regex ile basitçe buluyoruz, para birimi sembolleri dahil olabilir)
            # <div class="discount_final_price">$4.64</div>
            final_match = re.search(r'discount_final_price">([^<]+)</div>', content)
            final_price = final_match.group(1) if final_match else "?"
            
            orig_match = re.search(r'discount_original_price">([^<]+)</div>', content)
            orig_price = orig_match.group(1) if orig_match else "?"
            
            # Sadece geçerli indirimi olanları al
            # RV There Yet? (3949040) gibi sorunlu oyunları manuel filtrele (veya genel kural ekle)
            if discount > 0 and appid != "3949040":
                header_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
                candidates.append({
                    "appid": int(appid),
                    "name": name,
                    "discount": discount,
                    "final": final_price,
                    "orig": orig_price,
                    "url": f"https://store.steampowered.com/app/{appid}",
                    "header_image": header_url
                })
                
        return candidates

    except Exception as e:
        print(f"Arama API taraması sırasında hata: {e}")
        return []

def main():
    # Windows konsolunda Unicode karakterleri yazdırmak için (Crash önleyici)
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print(f"[{datetime.now()}] İndirimler kontrol ediliyor (Geniş Çaplı - Popülerlik Odaklı)...")
    sent = load_sent()
    
    # Yeni 'Search API' yöntemini kullan
    candidates = get_search_discounts()
    
    print(f"Bulunan toplam potansiyel fırsat sayısı: {len(candidates)}")

    if not candidates:
        print("Hiçbir fırsat bulunamadı.")
        return

    # ÖNEMLİ: İndirim oranına göre SIRALAMIYORUZ.
    # Steam API zaten 'Alaka Düzeyi' (Popülerlik/Uygunluk) sırasına göre veriyor.
    # Kullanıcı popüler oyunların önce paylaşılmasını istediği için bu sırayı koruyoruz.
    # candidates.sort(key=lambda x: x["discount"], reverse=True)  <-- BU SATIR KALDIRILDI

    # Henüz gönderilmemiş oyunu bul (Listedeki ilk eşleşen, en popüler olandır)
    target_game = None
    for game in candidates:
        if game["appid"] not in sent:
            target_game = game
            break
    
    if not target_game:
        print("Bulunan tüm fırsatlar zaten paylaşılmış.")
        return

    # Tweet oluştur ve gönder
    game = target_game
    text = (
        f"🔥 %{game['discount']} İNDİRİM!\n\n"
        f"🎮 {game['name']}\n"
        f"Eski Fiyat: {game['orig']}\n"
        f"Yeni Fiyat: {game['final']}\n\n"
        f"🛒 Link: {game['url']}\n\n"
        f"#Steam #Indirim #Oyun #GameDeals #PCGaming\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    print("-" * 30)
    print(f"Seçilen Oyun: {game['name']} (%{game['discount']})")
    print(f"Tweet İçeriği:\n{text}")
    print("-" * 30)
    
    try:
        # Resim indirme ve tweet atma işlemi
        image_path = "temp_game_image.jpg"
        media_id = None
        
        # Resim indirmeyi dene
        download_success = False
        if game.get("header_image"):
            try:
                print(f"Resim indiriliyor: {game['header_image']}")
                img_response = requests.get(game['header_image'], timeout=10)
                if img_response.status_code == 200:
                    with open(image_path, 'wb') as handler:
                        handler.write(img_response.content)
                    download_success = True
                else:
                    print(f"Resim indirilemedi (Status: {img_response.status_code}). Tweet resimsiz atılacak.")
            except Exception as e:
                 print(f"Resim indirme hatası: {e}")

        # Resmi Twitter'a yükle (Eğer indirme başarılıysa)
        if download_success:
            try:
                auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                api = tweepy.API(auth)
                media = api.media_upload(filename=image_path)
                media_id = media.media_id
                print(f"Resim Twitter'a yüklendi, ID: {media_id}")
            except Exception as img_err:
                print(f"Twitter resim yükleme hatası: {img_err}")
                media_id = None

        # Tweet at (Resimli veya resimsiz)
        import time
        import random
        # İnsan gibi davranmak için kısa bir bekleme ekle
        time.sleep(random.uniform(3, 7))
        
        if media_id:
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            print("Resimsiz tweet atılıyor...")
            response = client.create_tweet(text=text)
            
        print(f"Tweet Başarıyla Gönderildi! ID: {response.data['id']}")
        
        # Başarılı olursa listeye ekle
        sent.append(game["appid"])
        save_sent(sent)
        
        # Geçici resmi sil
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
            
    except Exception as e:
        print(f"Tweet atarken hata oluştu: {e}")
        
        is_duplicate = False
        error_msg = str(e).lower()
        
        # Hata detaylarını kontrol et
        if hasattr(e, 'response') and e.response is not None:
             print(f"Twitter API Hata Yanıtı: {e.response.text}")
             if "duplicate" in e.response.text.lower():
                 is_duplicate = True

        if "duplicate" in error_msg:
            is_duplicate = True

        # SADECE "Duplicate" (Tekrarlayan) hatası ise listeye ekleyip geçiyoruz.
        # Diğer hatalarda (Yetki yok, limit doldu vb.) listeye EKLEMİYORUZ ki sonra tekrar denesin.
        if is_duplicate:
            print(">>> BİLGİ: Bu tweet zaten atılmış. Listeye işleniyor.")
            sent.append(game["appid"])
            save_sent(sent)
        else:
            print(">>> UYARI: Tweet atılamadı ve 'Duplicate' hatası değil. Oyun listeye işlenmedi, sonra tekrar denenecek.")
            # 403 Forbidden genelde yetki/limit sorunudur.
            if "403" in error_msg:
                 print("!!! DİKKAT: 403 Forbidden hatası aldınız. API anahtarlarınızın yazma yetkisi olmayabilir veya limitiniz dolmuş olabilir.")

    print(f"[{datetime.now()}] İşlem tamamlandı.")

if __name__ == "__main__":
    main()
