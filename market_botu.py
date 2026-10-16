import json
import urllib.request
import re
from datetime import datetime

# EuroSpot Otomatik Pazar Verisi Uretici ve Test Kaziyicisi
# Lidl, Rewe ve Aldi gunluk / haftalik firsat verisi mimarisi

# Tum 27 Avrupa Birligi Uyesi Ulke ve Oncu Zincir Marketleri
EU_COUNTRIES = [
    {"code": "DE", "name": "Almanya", "chains": ["Lidl", "Aldi Süd", "Aldi Nord", "Rewe", "Edeka", "Kaufland", "Penny", "Netto"]},
    {"code": "FR", "name": "Fransa", "chains": ["Carrefour", "E.Leclerc", "Auchan", "Intermarché", "Monoprix", "Lidl FR", "Casino"]},
    {"code": "NL", "name": "Hollanda", "chains": ["Albert Heijn", "Jumbo", "Plus", "Lidl NL", "Dirk", "Aldi NL"]},
    {"code": "BE", "name": "Belçika", "chains": ["Delhaize", "Colruyt", "Carrefour BE", "Aldi BE", "Lidl BE"]},
    {"code": "AT", "name": "Avusturya", "chains": ["Billa", "Spar AT", "Hofer (Aldi)", "Penny AT", "Lidl AT"]},
    {"code": "IT", "name": "İtalya", "chains": ["Conad", "Coop", "Esselunga", "Eurospin", "Lidl IT", "Carrefour IT"]},
    {"code": "ES", "name": "İspanya", "chains": ["Mercadona", "Carrefour ES", "Lidl ES", "Dia", "Eroski", "Alcampo"]},
    {"code": "PL", "name": "Polonya", "chains": ["Biedronka", "Dino", "Lidl PL", "Kaufland PL", "Carrefour PL", "Auchan PL"]},
    {"code": "SE", "name": "İsveç", "chains": ["ICA", "Coop SE", "Willys", "City Gross", "Lidl SE"]},
    {"code": "DK", "name": "Danimarka", "chains": ["Netto DK", "Føtex", "Bilka", "Rema 1000", "Lidl DK", "Coop 365"]},
    {"code": "FI", "name": "Finlandiya", "chains": ["S-Market", "K-Citymarket", "Prisma", "Lidl FI", "Alepa"]},
    {"code": "IE", "name": "İrlanda", "chains": ["Tesco IE", "Dunnes Stores", "SuperValu", "Lidl IE", "Aldi IE"]},
    {"code": "PT", "name": "Portekiz", "chains": ["Continente", "Pingo Doce", "Auchan PT", "Lidl PT", "Intermarché PT"]},
    {"code": "GR", "name": "Yunanistan", "chains": ["Sklavenitis", "AB Vassilopoulos", "Lidl GR", "My Market", "Masoutis"]},
    {"code": "CZ", "name": "Çekya", "chains": ["Kaufland CZ", "Albert CZ", "Lidl CZ", "Billa CZ", "Penny CZ", "Tesco CZ"]},
    {"code": "HU", "name": "Macaristan", "chains": ["Spar HU", "Lidl HU", "Penny HU", "Tesco HU", "Auchan HU", "Aldi HU"]},
    {"code": "RO", "name": "Romanya", "chains": ["Kaufland RO", "Lidl RO", "Carrefour RO", "Mega Image", "Penny RO", "Auchan RO"]},
    {"code": "BG", "name": "Bulgaristan", "chains": ["Kaufland BG", "Lidl BG", "Billa BG", "Fantastico", "T-Market"]},
    {"code": "SK", "name": "Slovakya", "chains": ["Lidl SK", "Kaufland SK", "Billa SK", "Tesco SK", "Terno"]},
    {"code": "HR", "name": "Hırvatistan", "chains": ["Konzum", "Lidl HR", "Kaufland HR", "Spar HR", "Plodine", "Tommy"]},
    {"code": "SI", "name": "Slovenya", "chains": ["Mercator", "Spar SI", "Hofer SI", "Lidl SI", "Tuš"]},
    {"code": "LU", "name": "Lüksemburg", "chains": ["Cactus", "Auchan LU", "Delhaize LU", "Lidl LU", "Match"]},
    {"code": "EE", "name": "Estonya", "chains": ["Selver", "Maxima EE", "Rimi EE", "Prisma EE", "Coop EE", "Lidl EE"]},
    {"code": "LV", "name": "Letonya", "chains": ["Rimi LV", "Maxima LV", "Lidl LV", "Mego", "top!"]},
    {"code": "LT", "name": "Litvanya", "chains": ["Maxima LT", "IKI", "Lidl LT", "Norfa", "Rimi LT"]},
    {"code": "CY", "name": "Kıbrıs Rum Kesimi", "chains": ["Alphamega", "Lidl CY", "Metro CY", "Sklavenitis CY"]},
    {"code": "MT", "name": "Malta", "chains": ["Lidl MT", "Wellbees", "Greens Supermarket", "Pavi-Pama"]}
]

def generate_germany_deals():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Kapsamli AB Firsatlari Veri Seti (Tum Birlik Icin Coklu Ulke Akisi)
    deals = [
        # Almanya (DE)
        {"country": "DE", "name": "Bio Vollmilch 3.8% (Organik Sut)", "store": "Rewe", "originalPrice": 1.79, "discountedPrice": 1.19, "unit": "1 Litre", "distance": "Rewe City (0.8 km)", "eveningClearance": False},
        {"country": "DE", "name": "Gouda Jung am Stuck (Taze Gouda)", "store": "Lidl", "originalPrice": 3.99, "discountedPrice": 2.49, "unit": "400g Blok", "distance": "Lidl Filiale (1.2 km)", "eveningClearance": False},
        {"country": "DE", "name": "Frisches Hähnchenbrustfilet (Tavuk)", "store": "Aldi Süd", "originalPrice": 7.49, "discountedPrice": 4.99, "unit": "600g", "distance": "Aldi Süd (1.5 km)", "eveningClearance": True},
        {"country": "DE", "name": "Deutsches Roggenmischbrot (Cavdar)", "store": "Lidl", "originalPrice": 1.89, "discountedPrice": 0.99, "unit": "1 kg", "distance": "Lidl Filiale (1.2 km)", "eveningClearance": True},
        {"country": "DE", "name": "Lavazza Caffe Crema Classico", "store": "Rewe", "originalPrice": 15.99, "discountedPrice": 9.99, "unit": "1000g", "distance": "Rewe Center (2.1 km)", "eveningClearance": False},
        {"country": "DE", "name": "Nutella Fındık Kreması XL", "store": "Aldi Nord", "originalPrice": 4.49, "discountedPrice": 2.89, "unit": "750g", "distance": "Aldi Nord (2.8 km)", "eveningClearance": False},
        {"country": "DE", "name": "Barilla Spaghetti No.5", "store": "Lidl", "originalPrice": 1.99, "discountedPrice": 0.88, "unit": "500g", "distance": "Lidl Filiale (1.2 km)", "eveningClearance": False},
        {"country": "DE", "name": "Ariel Pods All-in-1 Kapsül", "store": "Rewe", "originalPrice": 12.99, "discountedPrice": 8.49, "unit": "38 Yıkama", "distance": "Rewe Center (2.1 km)", "eveningClearance": False},
        
        # Fransa (FR)
        {"country": "FR", "name": "Baguette Tradition Française", "store": "Carrefour", "originalPrice": 1.30, "discountedPrice": 0.75, "unit": "250g", "distance": "Carrefour Market (1.1 km)", "eveningClearance": True},
        {"country": "FR", "name": "Fromage Camembert de Normandie", "store": "E.Leclerc", "originalPrice": 2.89, "discountedPrice": 1.69, "unit": "250g", "distance": "E.Leclerc (2.4 km)", "eveningClearance": False},
        {"country": "FR", "name": "Croissant Pur Beurre (4'lü)", "store": "Auchan", "originalPrice": 2.60, "discountedPrice": 1.49, "unit": "Paket", "distance": "Auchan Super (1.8 km)", "eveningClearance": True},
        {"country": "FR", "name": "L'Or Espresso Kapsül Kahve", "store": "Carrefour", "originalPrice": 4.19, "discountedPrice": 2.79, "unit": "10 Kapsül", "distance": "Carrefour Market (1.1 km)", "eveningClearance": False},

        # Hollanda (NL)
        {"country": "NL", "name": "Goudse Belegen Kaas (Gouda)", "store": "Albert Heijn", "originalPrice": 5.49, "discountedPrice": 3.49, "unit": "450g", "distance": "Albert Heijn XL (0.9 km)", "eveningClearance": False},
        {"country": "NL", "name": "Stroopwafels Karamelli Waffle", "store": "Jumbo", "originalPrice": 2.49, "discountedPrice": 1.39, "unit": "10 Adet", "distance": "Jumbo Supermarkt (1.4 km)", "eveningClearance": False},
        {"country": "NL", "name": "Verse Halfvolle Melk (Yarım Yağlı Süt)", "store": "Plus", "originalPrice": 1.45, "discountedPrice": 0.95, "unit": "1.5 Litre", "distance": "Plus Markt (2.0 km)", "eveningClearance": True},

        # Belçika (BE)
        {"country": "BE", "name": "Belgian Waffles (Liege Şekerli)", "store": "Delhaize", "originalPrice": 3.20, "discountedPrice": 1.99, "unit": "5x90g", "distance": "Delhaize Super (1.3 km)", "eveningClearance": False},
        {"country": "BE", "name": "Côte d'Or Lait Noisettes Çikolata", "store": "Colruyt", "originalPrice": 3.89, "discountedPrice": 2.39, "unit": "2x150g", "distance": "Colruyt Meest (2.5 km)", "eveningClearance": False},

        # Avusturya (AT)
        {"country": "AT", "name": "Tiroler Bergkäse Dağ Peyniri", "store": "Billa", "originalPrice": 4.29, "discountedPrice": 2.79, "unit": "250g", "distance": "Billa Plus (1.0 km)", "eveningClearance": False},
        {"country": "AT", "name": "Manner Original Neapolitaner Gofret", "store": "Spar AT", "originalPrice": 3.99, "discountedPrice": 2.49, "unit": "4x75g", "distance": "Interspar (1.7 km)", "eveningClearance": False},
        {"country": "AT", "name": "Bio Bergbauern Heumilch Süt", "store": "Hofer (Aldi)", "originalPrice": 1.69, "discountedPrice": 1.15, "unit": "1 Litre", "distance": "Hofer Filiale (1.2 km)", "eveningClearance": True},

        # İtalya (IT)
        {"country": "IT", "name": "Parmigiano Reggiano DOP 24 Ay", "store": "Conad", "originalPrice": 6.90, "discountedPrice": 4.49, "unit": "300g", "distance": "Conad Superstore (1.5 km)", "eveningClearance": False},
        {"country": "IT", "name": "Olio Extra Vergine di Oliva Sızma", "store": "Coop", "originalPrice": 9.80, "discountedPrice": 6.30, "unit": "1 Litre", "distance": "IperCoop (2.8 km)", "eveningClearance": False},

        # İspanya (ES)
        {"country": "ES", "name": "Jamón Serrano Reserva Dilimli", "store": "Mercadona", "originalPrice": 3.20, "discountedPrice": 1.99, "unit": "150g", "distance": "Mercadona (0.7 km)", "eveningClearance": False},
        {"country": "ES", "name": "Aceite de Oliva Virgen Extra", "store": "Carrefour ES", "originalPrice": 8.95, "discountedPrice": 5.95, "unit": "1 Litre", "distance": "Carrefour Hyper (2.2 km)", "eveningClearance": False},

        # Polonya (PL)
        {"country": "PL", "name": "Twaróg Półtłusty Taze Çökelek", "store": "Biedronka", "originalPrice": 1.25, "discountedPrice": 0.79, "unit": "250g", "distance": "Biedronka (0.6 km)", "eveningClearance": False},
        {"country": "PL", "name": "Kiełbasa Śląska Sosis", "store": "Dino", "originalPrice": 4.10, "discountedPrice": 2.60, "unit": "500g", "distance": "Dino Market (1.3 km)", "eveningClearance": True}
    ]
    
    feed = {
        "updated_at": now,
        "region": "European Union (EU-27)",
        "currency": "EUR",
        "supported_countries_count": len(EU_COUNTRIES),
        "supported_countries": EU_COUNTRIES,
        "deals_count": len(deals),
        "deals": deals
    }
    
    with open("germany_deals.json", "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
        
    print(f"Basarili: 27 AB ulkesi mimarisi ve {len(deals)} adet cok ulkeli market firsati germany_deals.json dosyasina yazildi.")

if __name__ == "__main__":
    generate_germany_deals()
