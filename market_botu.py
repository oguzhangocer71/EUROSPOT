import json
import urllib.request
import re
from datetime import datetime

# EuroSpot Otomatik Pazar Verisi Uretici ve Test Kaziyicisi
# Lidl, Rewe ve Aldi gunluk / haftalik firsat verisi mimarisi

def generate_germany_deals():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Gercekci ve pazar verisi bazli guncel ornek veri seti
    deals = [
        {
            "name": "Bio Vollmilch 3.8% (Organik Sut)",
            "store": "Rewe",
            "originalPrice": 1.79,
            "discountedPrice": 1.19,
            "unit": "1 Litre",
            "distance": "Rewe City (0.8 km)",
            "eveningClearance": False
        },
        {
            "name": "Gouda Jung am Stuck (Taze Gouda)",
            "store": "Lidl",
            "originalPrice": 3.99,
            "discountedPrice": 2.49,
            "unit": "400g Blok",
            "distance": "Lidl Filiale (1.2 km)",
            "eveningClearance": False
        },
        {
            "name": "Frisches Hähnchenbrustfilet (Tavuk Gogsu)",
            "store": "Aldi Süd",
            "originalPrice": 7.49,
            "discountedPrice": 4.99,
            "unit": "600g",
            "distance": "Aldi Süd (1.5 km)",
            "eveningClearance": True
        },
        {
            "name": "Deutsches Roggenmischbrot (Cavdar Ekmegi)",
            "store": "Lidl",
            "originalPrice": 1.89,
            "discountedPrice": 0.99,
            "unit": "1 kg Somun",
            "distance": "Lidl Filiale (1.2 km)",
            "eveningClearance": True
        },
        {
            "name": "Lavazza Caffe Crema Classico Çekirdek Kahve",
            "store": "Rewe",
            "originalPrice": 15.99,
            "discountedPrice": 9.99,
            "unit": "1000g Paket",
            "distance": "Rewe Center (2.1 km)",
            "eveningClearance": False
        },
        {
            "name": "Nutella Fındık Kreması XL",
            "store": "Aldi Nord",
            "originalPrice": 4.49,
            "discountedPrice": 2.89,
            "unit": "750g Kavanoz",
            "distance": "Aldi Nord (2.8 km)",
            "eveningClearance": False
        },
        {
            "name": "Barilla Spaghetti No.5 Makarna",
            "store": "Lidl",
            "originalPrice": 1.99,
            "discountedPrice": 0.88,
            "unit": "500g",
            "distance": "Lidl Filiale (1.2 km)",
            "eveningClearance": False
        },
        {
            "name": "Ariel Pods All-in-1 Çamaşır Kapsülü",
            "store": "Rewe",
            "originalPrice": 12.99,
            "discountedPrice": 8.49,
            "unit": "38 Yıkama",
            "distance": "Rewe Center (2.1 km)",
            "eveningClearance": False
        }
    ]
    
    feed = {
        "updated_at": now,
        "region": "Germany (DE)",
        "currency": "EUR",
        "deals_count": len(deals),
        "deals": deals
    }
    
    with open("germany_deals.json", "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
        
    print(f"Basarili: {len(deals)} adet market firsati germany_deals.json dosyasina yazildi.")

if __name__ == "__main__":
    generate_germany_deals()
