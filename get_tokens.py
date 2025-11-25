import tweepy

def main():
    print("--- TWITTER HESAP DEĞİŞTİRME ARACI ---")
    print("Bu araç, mevcut botunuzu BAŞKA bir Twitter hesabına bağlamanızı sağlar.")
    print("Lütfen GitHub Secrets kısmında kayıtlı olan API Key ve Secret'ınızı hazırlayın.\n")

    api_key = input("API Key (Consumer Key) girin: ").strip()
    api_secret = input("API Secret (Consumer Secret) girin: ").strip()

    if not api_key or not api_secret:
        print("Hata: Key veya Secret boş olamaz.")
        return

    try:
        # OAuth 1.0a User Context (PIN-based auth)
        oauth1_user_handler = tweepy.OAuth1UserHandler(
            api_key, api_secret, callback="oob"
        )
        
        auth_url = oauth1_user_handler.get_authorization_url()
        
        print("\n" + "="*60)
        print("LÜTFEN ŞU ADIMLARI TAKİP EDİN:")
        print("1. Aşağıdaki linke tıklayın (Tarayıcıda açılacak).")
        print("2. Hangi hesaptan tweet atılmasını istiyorsanız O HESAPLA giriş yapın.")
        print("3. 'Uygulamaya İzin Ver' butonuna basın.")
        print("4. Size verilen 7 haneli PIN kodunu kopyalayın.")
        print("="*60)
        print(f"\nLİNK: {auth_url}\n")
        
        verifier = input("PIN Kodunu buraya yapıştırın ve Enter'a basın: ").strip()
        
        access_token, access_token_secret = oauth1_user_handler.get_access_token(verifier)
        
        print("\n" + "="*60)
        print("✅ BAŞARILI! İŞTE YENİ HESABINIZIN ŞİFRELERİ:")
        print("="*60)
        print(f"ACCESS_TOKEN: {access_token}")
        print(f"ACCESS_TOKEN_SECRET: {access_token_secret}")
        print("="*60)
        print("\nYAPMANIZ GEREKEN:")
        print("1. GitHub Deponuz -> Settings -> Secrets -> Actions kısmına gidin.")
        print("2. 'ACCESS_TOKEN' ve 'ACCESS_TOKEN_SECRET' değerlerini bu yenileriyle güncelleyin.")
        print("3. API_KEY ve API_SECRET aynı kalacak, onlara dokunmayın.")
        
    except Exception as e:
        print(f"\nHata oluştu: {e}")
        print("Lütfen API Key ve Secret'ın doğru olduğundan emin olun.")

if __name__ == "__main__":
    main()
