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

def tweet(text):
    """X API (Tweepy) kullanarak tweet atar."""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("UYARI: API anahtarları eksik. Tweet atılamıyor (Test modu).")
        print(f"Tweet İçeriği:\n{text}")
        return

    try:
        # X API v2 Client (Free Tier için v2 kullanılır)
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        response = client.create_tweet(text=text)
        print(f"Tweet Başarıyla Gönderildi! ID: {response.data['id']}")
        
    except Exception as e:
        print(f"Tweet Gönderme Hatası: {e}")


def get_discounted_games(app_ids):
    """Verilen App ID listesindeki oyunların indirim durumunu kontrol eder."""
    discounted = []

    for appid in app_ids:
        try:
            # Ancak Steam API bazen tutarsız olabilir, en garantisi tüm veriyi çekip parse etmek.
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us"
            response = requests.get(url, timeout=10)
            data = response.json()

            if not data or str(appid) not in data or not data[str(appid)]["success"]:
                print(f"Oyun verisi alınamadı: {appid}")
                continue
            
            app_data = data[str(appid)]["data"]
            price_data = app_data.get("price_overview")
            
            # Ücretsiz oyunlar veya fiyatı olmayanlar için kontrol
            if not price_data:
                continue

            discount = price_data["discount_percent"]
            if discount > 0:
                discounted.append({
                    "appid": appid,
                    "name": app_data.get("name", "Steam Oyunu"),
                    "discount": discount,
                    "final": price_data["final_formatted"],
                    "orig": price_data["initial_formatted"],
                    "url": f"https://store.steampowered.com/app/{appid}"
                })
        except Exception as e:
            print(f"Hata ({appid}): {e}")

    return discounted


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


def get_steam_specials():
    """Steam 'Özel Fırsatlar' sayfasından indirimli oyunları çeker."""
    url = "https://store.steampowered.com/api/featuredcategories?cc=us&l=english"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        specials = []
        # 'specials' kategorisi altındaki oyunları al
        if "specials" in data and "items" in data["specials"]:
            for item in data["specials"]["items"]:
                # Sadece oyunları al (type 0 = oyun, type 1 = paket)
                # İndirim oranı %20'den büyük olanları alalım
                if item.get("discount_percent", 0) >= 20:
                    specials.append({
                        "appid": item["id"],
                        "name": item["name"],
                        "discount": item["discount_percent"],
                        "final": f"${item['final_price'] / 100:.2f}", # Fiyat kuruş cinsinden gelir
                        "orig": f"${item['original_price'] / 100:.2f}",
                        "url": f"https://store.steampowered.com/app/{item['id']}"
                    })
        return specials
    except Exception as e:
        print(f"Steam Specials çekilirken hata: {e}")
        return []

def main():
    print(f"[{datetime.now()}] İndirimler kontrol ediliyor (Dinamik Mod)...")
    sent = load_sent()
    
    # Dinamik olarak indirimleri çek
    candidates = get_steam_specials()
    print(f"Bulunan potansiyel fırsat sayısı: {len(candidates)}")

    if not candidates:
        print("Hiçbir fırsat bulunamadı.")
        return

    # İndirim oranına göre sırala (En yüksekten en düşüğe)
    candidates.sort(key=lambda x: x["discount"], reverse=True)

    # Henüz gönderilmemiş EN İYİ fırsatı bul
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
        f"#Steam #Indirim #Oyun #GameDeals #PCGaming"
    )
    
    print("-" * 30)
    print(f"Seçilen Oyun: {game['name']} (%{game['discount']})")
    print(f"Tweet İçeriği:\n{text}")
    print("-" * 30)
    
    try:
        tweet(text)
        # Başarılı olursa listeye ekle
        sent.append(game["appid"])
        save_sent(sent)
    except Exception as e:
        print(f"Tweet atarken hata oluştu: {e}")
        # Eğer hata "Duplicate" ise (403), yine de gönderildi sayalım
        if "duplicate" in str(e).lower() or "403" in str(e):
            print("Bu tweet zaten atılmış, listeye işleniyor.")
            sent.append(game["appid"])
            save_sent(sent)

    print(f"[{datetime.now()}] İşlem tamamlandı.")

if __name__ == "__main__":
    main()
