import json
import random
from datetime import datetime

COUNTRIES = [
    {"code": "DE", "name": "Almanya", "flag": "🇩🇪", "chains": ["Lidl", "Aldi Süd", "Aldi Nord", "Rewe", "Edeka", "Kaufland", "Penny", "Netto"]},
    {"code": "FR", "name": "Fransa", "flag": "🇫🇷", "chains": ["Carrefour", "E.Leclerc", "Auchan", "Intermarché", "Monoprix", "Casino"]},
    {"code": "NL", "name": "Hollanda", "flag": "🇳🇱", "chains": ["Albert Heijn", "Jumbo", "Plus", "Dirk", "Aldi NL"]},
    {"code": "BE", "name": "Belçika", "flag": "🇧🇪", "chains": ["Delhaize", "Colruyt", "Carrefour BE", "Aldi BE"]},
    {"code": "AT", "name": "Avusturya", "flag": "🇦🇹", "chains": ["Billa", "Spar AT", "Hofer (Aldi)", "Penny AT"]},
    {"code": "IT", "name": "İtalya", "flag": "🇮🇹", "chains": ["Conad", "Coop IT", "Esselunga", "Eurospin", "Carrefour IT"]},
    {"code": "ES", "name": "İspanya", "flag": "🇪🇸", "chains": ["Mercadona", "Carrefour ES", "Dia", "Eroski", "Alcampo"]},
    {"code": "PL", "name": "Polonya", "flag": "🇵🇱", "chains": ["Biedronka", "Dino", "Kaufland PL", "Lidl PL", "Carrefour PL"]},
    {"code": "SE", "name": "İsveç", "flag": "🇸🇪", "chains": ["ICA", "Coop SE", "Willys", "City Gross"]},
    {"code": "DK", "name": "Danimarka", "flag": "🇩🇰", "chains": ["Netto DK", "Føtex", "Bilka", "Rema 1000"]},
    {"code": "FI", "name": "Finlandiya", "flag": "🇫🇮", "chains": ["S-Market", "K-Citymarket", "Prisma", "Alepa"]},
    {"code": "IE", "name": "İrlanda", "flag": "🇮🇪", "chains": ["Tesco IE", "Dunnes Stores", "SuperValu", "Aldi IE"]},
    {"code": "PT", "name": "Portekiz", "flag": "🇵🇹", "chains": ["Continente", "Pingo Doce", "Auchan PT", "Intermarché PT"]},
    {"code": "GR", "name": "Yunanistan", "flag": "🇬🇷", "chains": ["Sklavenitis", "AB Vassilopoulos", "My Market", "Masoutis"]},
    {"code": "CZ", "name": "Çekya", "flag": "🇨🇿", "chains": ["Albert CZ", "Billa CZ", "Penny CZ", "Tesco CZ"]},
    {"code": "HU", "name": "Macaristan", "flag": "🇭🇺", "chains": ["Spar HU", "Penny HU", "Tesco HU", "Aldi HU"]},
    {"code": "RO", "name": "Romanya", "flag": "🇷🇴", "chains": ["Mega Image", "Penny RO", "Kaufland RO", "Carrefour RO"]},
    {"code": "BG", "name": "Bulgaristan", "flag": "🇧🇬", "chains": ["Billa BG", "Fantastico", "T-Market", "Kaufland BG"]},
    {"code": "HR", "name": "Hırvatistan", "flag": "🇭🇷", "chains": ["Konzum", "Spar HR", "Plodine", "Tommy"]},
    {"code": "SK", "name": "Slovakya", "flag": "🇸🇰", "chains": ["Billa SK", "Tesco SK", "Terno", "Kaufland SK"]},
    {"code": "SI", "name": "Slovenya", "flag": "🇸🇮", "chains": ["Mercator", "Spar SI", "Hofer SI", "Tuš"]},
    {"code": "LU", "name": "Lüksemburg", "flag": "🇱🇺", "chains": ["Cactus", "Auchan LU", "Delhaize LU", "Match"]},
    {"code": "EE", "name": "Estonya", "flag": "🇪🇪", "chains": ["Selver", "Maxima EE", "Rimi EE", "Coop EE"]},
    {"code": "LV", "name": "Letonya", "flag": "🇱🇻", "chains": ["Rimi LV", "Maxima LV", "Mego", "top!"]},
    {"code": "LT", "name": "Litvanya", "flag": "🇱🇹", "chains": ["Maxima LT", "IKI", "Norfa", "Rimi LT"]},
    {"code": "CY", "name": "Kıbrıs", "flag": "🇨🇾", "chains": ["Alphamega", "Metro CY", "Sklavenitis CY"]},
    {"code": "MT", "name": "Malta", "flag": "🇲🇹", "chains": ["Wellbees", "Greens Supermarket", "Pavi-Pama"]}
]

# Zengin Kategori ve Urun Sablonlari
CATALOG_ITEMS = [
    # Süt & Kahvaltılık
    {"name": "Bio Vollmilch 3.8%", "cat": "Süt & Kahvaltılık", "orig": 1.79, "disc": 1.19, "unit": "1 Litre"},
    {"name": "Gouda Jung Käse Scheiben", "cat": "Süt & Kahvaltılık", "orig": 2.99, "disc": 1.89, "unit": "400g"},
    {"name": "Kerrygold Irische Butter", "cat": "Süt & Kahvaltılık", "orig": 3.49, "disc": 2.19, "unit": "250g"},
    {"name": "Müllermilch Schoko & Erdbeer", "cat": "Süt & Kahvaltılık", "orig": 1.49, "disc": 0.89, "unit": "500ml"},
    {"name": "Nutella Nuss-Nugat-Creme", "cat": "Süt & Kahvaltılık", "orig": 4.59, "disc": 2.99, "unit": "750g"},
    {"name": "Frische Freilandeier (Gezegen Yumurta)", "cat": "Süt & Kahvaltılık", "orig": 3.29, "disc": 2.19, "unit": "10'lu Kutu"},
    {"name": "Griechischer Joghurt 10%", "cat": "Süt & Kahvaltılık", "orig": 2.49, "disc": 1.59, "unit": "500g"},
    {"name": "Arla Buko Der Sahnige Frischkäse", "cat": "Süt & Kahvaltılık", "orig": 2.19, "disc": 1.29, "unit": "200g"},
    {"name": "Philadelphia Frischkäse Classic", "cat": "Süt & Kahvaltılık", "orig": 2.49, "disc": 1.49, "unit": "175g"},
    {"name": "Parmigiano Reggiano DOP 24 Ay", "cat": "Süt & Kahvaltılık", "orig": 6.89, "disc": 4.69, "unit": "200g"},
    {"name": "Président Camembert l'Aromatique", "cat": "Süt & Kahvaltılık", "orig": 3.69, "disc": 2.39, "unit": "250g"},
    {"name": "Danone Activia Erdbeere Joghurt", "cat": "Süt & Kahvaltılık", "orig": 2.79, "disc": 1.89, "unit": "4x115g"},
    {"name": "Twaróg Półtłusty (Geleneksel Lor Peyniri)", "cat": "Süt & Kahvaltılık", "orig": 2.19, "disc": 1.39, "unit": "250g"},
    {"name": "Edamer Käse Block 40% F.i.Tr.", "cat": "Süt & Kahvaltılık", "orig": 4.29, "disc": 2.79, "unit": "400g"},
    {"name": "Bio Hafermilch Barista Edition", "cat": "Süt & Kahvaltılık", "orig": 2.29, "disc": 1.49, "unit": "1 Litre"},

    # Et & Şarküteri
    {"name": "Frisches Hähnchenbrustfilet (Tavuk Göğsü)", "cat": "Et & Şarküteri", "orig": 8.99, "disc": 5.99, "unit": "600g"},
    {"name": "Rinderhackfleisch Frisch (Dana Kıyma)", "cat": "Et & Şarküteri", "orig": 7.49, "disc": 4.99, "unit": "500g"},
    {"name": "Schwarzwälder Schinken IGP", "cat": "Et & Şarküteri", "orig": 2.89, "disc": 1.79, "unit": "100g"},
    {"name": "Wiener Würstchen im Saitling", "cat": "Et & Şarküteri", "orig": 3.99, "disc": 2.59, "unit": "400g (6 Adet)"},
    {"name": "Jamón Serrano Reserva 14 Ay", "cat": "Et & Şarküteri", "orig": 4.29, "disc": 2.89, "unit": "120g"},
    {"name": "Kiełbasa Krakowska Sucha", "cat": "Et & Şarküteri", "orig": 5.19, "disc": 3.49, "unit": "350g"},
    {"name": "Rumpsteak vom Jungbullen (Dana Biftek)", "cat": "Et & Şarküteri", "orig": 12.90, "disc": 8.99, "unit": "300g"},
    {"name": "Lachsfilet mit Haut Frisch (Taze Somon)", "cat": "Et & Şarküteri", "orig": 9.99, "disc": 6.89, "unit": "300g"},
    {"name": "Putenbrustaufschnitt Zart & Mager", "cat": "Et & Şarküteri", "orig": 2.59, "disc": 1.69, "unit": "150g"},
    {"name": "Grobe Bratwurst Fränkische Art", "cat": "Et & Şarküteri", "orig": 4.49, "disc": 2.99, "unit": "400g"},

    # Meyve & Sebze
    {"name": "Bio Bananen Fairtrade", "cat": "Meyve & Sebze", "orig": 2.19, "disc": 1.29, "unit": "1 kg"},
    {"name": "Spanische Avocados Hass Ready-to-Eat", "cat": "Meyve & Sebze", "orig": 2.99, "disc": 1.79, "unit": "2'li Paket"},
    {"name": "Kulturheidelbeeren Frisch (Yaban Mersini)", "cat": "Meyve & Sebze", "orig": 3.49, "disc": 2.19, "unit": "300g"},
    {"name": "Rispmentomaten Rot & Saftig (Salkım Domates)", "cat": "Meyve & Sebze", "orig": 2.89, "disc": 1.69, "unit": "1 kg"},
    {"name": "Eisbergsalat Kl. I (Göbek Marul)", "cat": "Meyve & Sebze", "orig": 1.49, "disc": 0.79, "unit": "1 Adet"},
    {"name": "Gala Äpfel Knackig Süß (Elma)", "cat": "Meyve & Sebze", "orig": 3.29, "disc": 1.99, "unit": "2 kg Beutel"},
    {"name": "Mini Gurken Snack (Çıtır Hıyar)", "cat": "Meyve & Sebze", "orig": 1.99, "disc": 1.19, "unit": "400g"},
    {"name": "Speisekartoffeln Vorwiegend Festkochend", "cat": "Meyve & Sebze", "orig": 3.99, "disc": 2.49, "unit": "2.5 kg Çuval"},
    {"name": "Clementinen Süß & Kernlos (Mandalina)", "cat": "Meyve & Sebze", "orig": 2.99, "disc": 1.79, "unit": "1 kg File"},
    {"name": "Frische Champignons Weiß (Mantar)", "cat": "Meyve & Sebze", "orig": 2.29, "disc": 1.39, "unit": "400g"},

    # Fırın & Ekmek
    {"name": "Steinofenbaguette Knusprig", "cat": "Fırın & Ekmek", "orig": 1.39, "disc": 0.79, "unit": "250g"},
    {"name": "Buttercroissants Frisch Gebacken", "cat": "Fırın & Ekmek", "orig": 2.49, "disc": 1.49, "unit": "4x60g"},
    {"name": "Vollkorn Roggenbrot (Tam Çavdar Ekmeği)", "cat": "Fırın & Ekmek", "orig": 2.29, "disc": 1.39, "unit": "500g"},
    {"name": "Original Holländische Stroopwafels", "cat": "Fırın & Ekmek", "orig": 2.69, "disc": 1.69, "unit": "315g (8'li)"},
    {"name": "Toastbrot Golden Toast American Style", "cat": "Fırın & Ekmek", "orig": 1.99, "disc": 1.29, "unit": "500g"},
    {"name": "Laugenbrezeln Frischepackung", "cat": "Fırın & Ekmek", "orig": 2.19, "disc": 1.39, "unit": "4 Adet"},
    {"name": "Donuts mit Pink Icing & Streuseln", "cat": "Fırın & Ekmek", "orig": 2.79, "disc": 1.69, "unit": "4'lü Kutu"},

    # Temel Gıda & Bakliyat
    {"name": "Barilla Spaghetti N.5", "cat": "Temel Gıda & Bakliyat", "orig": 2.09, "disc": 1.11, "unit": "500g"},
    {"name": "Natives Olivenöl Extra Vergine", "cat": "Temel Gıda & Bakliyat", "orig": 9.99, "disc": 6.79, "unit": "750ml"},
    {"name": "Basmati Reis Premium Langkorn", "cat": "Temel Gıda & Bakliyat", "orig": 3.49, "disc": 2.29, "unit": "1 kg"},
    {"name": "Mutti Polpa Geschälte Tomaten", "cat": "Temel Gıda & Bakliyat", "orig": 1.79, "disc": 1.09, "unit": "400g"},
    {"name": "Sonnenblumenöl Rein (Ayçiçek Yağı)", "cat": "Temel Gıda & Bakliyat", "orig": 2.49, "disc": 1.69, "unit": "1 Litre"},
    {"name": "Weizenmehl Type 405 (Buğday Unu)", "cat": "Temel Gıda & Bakliyat", "orig": 1.19, "disc": 0.69, "unit": "1 kg"},
    {"name": "Rote Linsen Fein (Kırmızı Mercimek)", "cat": "Temel Gıda & Bakliyat", "orig": 2.19, "disc": 1.39, "unit": "500g"},
    {"name": "Thunfischfilets in Olivenöl", "cat": "Temel Gıda & Bakliyat", "orig": 3.89, "disc": 2.49, "unit": "3x80g"},
    {"name": "Bio Kichererbsen im Glas (Nohut)", "cat": "Temel Gıda & Bakliyat", "orig": 1.69, "disc": 0.99, "unit": "370ml"},

    # İçecek & Kahve
    {"name": "Lavazza Caffè Crema e Aroma Bohnen", "cat": "İçecek & Kahve", "orig": 16.99, "disc": 10.99, "unit": "1 kg Çekirdek"},
    {"name": "Jacobs Krönung Gemahlener Kaffee", "cat": "İçecek & Kahve", "orig": 7.49, "disc": 4.44, "unit": "500g"},
    {"name": "Coca-Cola Original Taste / Zero Kasten", "cat": "İçecek & Kahve", "orig": 14.49, "disc": 9.99, "unit": "12x1L (+Pfand)"},
    {"name": "Red Bull Energy Drink", "cat": "İçecek & Kahve", "orig": 1.49, "disc": 0.95, "unit": "250ml (+Pfand)"},
    {"name": "San Pellegrino Mineralwasser Kasten", "cat": "İçecek & Kahve", "orig": 8.99, "disc": 5.99, "unit": "6x1L Glas"},
    {"name": "Innocent Super Smoothie Plus Vitamin", "cat": "İçecek & Kahve", "orig": 3.49, "disc": 2.19, "unit": "300ml"},
    {"name": "Teekanne Kamillentee / Pfefferminze", "cat": "İçecek & Kahve", "orig": 2.29, "disc": 1.39, "unit": "20 Poşet"},
    {"name": "Paulaner Hefe-Weißbier Naturtrüb", "cat": "İçecek & Kahve", "orig": 18.99, "disc": 13.99, "unit": "20x0.5L Kasten"},

    # Atıştırmalık & Tatlı
    {"name": "Milka Alpenmilch Schokolade Tafeln", "cat": "Atıştırmalık & Tatlı", "orig": 1.49, "disc": 0.79, "unit": "100g"},
    {"name": "Pringles Original / Sour Cream & Onion", "cat": "Atıştırmalık & Tatlı", "orig": 2.99, "disc": 1.69, "unit": "185g"},
    {"name": "Haribo Goldbären Fruchtgummi", "cat": "Atıştırmalık & Tatlı", "orig": 1.29, "disc": 0.69, "unit": "175g"},
    {"name": "Ferrero Rocher Pralinen Box", "cat": "Atıştırmalık & Tatlı", "orig": 4.49, "disc": 2.99, "unit": "200g (16 Adet)"},
    {"name": "Lay's Paprika Kartoffelchips", "cat": "Atıştırmalık & Tatlı", "orig": 2.19, "disc": 1.29, "unit": "150g"},
    {"name": "Ritter Sport Bunte Vielfalt Schoko", "cat": "Atıştırmalık & Tatlı", "orig": 1.59, "disc": 0.88, "unit": "100g"},
    {"name": "Kinder Bueno Riegel Multipack", "cat": "Atıştırmalık & Tatlı", "orig": 2.89, "disc": 1.89, "unit": "6'lı Paket"},

    # Temizlik & Hijyen
    {"name": "Ariel All-in-1 PODS Color Waschmittel", "cat": "Temizlik & Hijyen", "orig": 19.99, "disc": 13.99, "unit": "60 Yıkama"},
    {"name": "Persil Universal Kraft-Gel Flüssig", "cat": "Temizlik & Hijyen", "orig": 18.49, "disc": 12.49, "unit": "50 Yıkama"},
    {"name": "Finish Quantum Ultimate Spülmaschinentabs", "cat": "Temizlik & Hijyen", "orig": 14.99, "disc": 9.99, "unit": "45 Tablet"},
    {"name": "Fairy Ultra Spülmittel Konzentrat", "cat": "Temizlik & Hijyen", "orig": 2.49, "disc": 1.49, "unit": "450ml"},
    {"name": "Lenor Weichspüler Frischeschutz", "cat": "Temizlik & Hijyen", "orig": 3.79, "disc": 2.29, "unit": "800ml (32 Yıkama)"},
    {"name": "Colgate Total Zahncreme Original", "cat": "Temizlik & Hijyen", "orig": 2.99, "disc": 1.69, "unit": "75ml"},
    {"name": "Nivea Duschgel Pflegend Verwöhnend", "cat": "Temizlik & Hijyen", "orig": 2.49, "disc": 1.49, "unit": "250ml"},
    {"name": "Zewa Ultra Soft Toilettenpapier 4-Lagig", "cat": "Temizlik & Hijyen", "orig": 5.99, "disc": 3.89, "unit": "8 Rulo"},
    {"name": "Domestos WC-Blitz Gel Kraftreiniger", "cat": "Temizlik & Hijyen", "orig": 2.39, "disc": 1.49, "unit": "750ml"}
]

total_target = 1000
all_deals = []

# Her ulkeden dengeli ve gercekci dagilim
items_per_country = total_target // len(COUNTRIES)
extra = total_target % len(COUNTRIES)

deal_id = 1
for i, c in enumerate(COUNTRIES):
    c_count = items_per_country + (1 if i < extra else 0)
    for j in range(c_count):
        template = random.choice(CATALOG_ITEMS)
        chain = random.choice(c["chains"])
        
        # Fiyatlarda ufak varyasyonlar
        disc_var = round(template["disc"] * random.uniform(0.92, 1.10), 2)
        orig_var = round(disc_var * random.uniform(1.30, 1.55), 2)
        
        # Mesafe ve aksam indirimi
        dist_num = round(random.uniform(0.3, 4.5), 1)
        is_evening = random.random() < 0.20 # %20 ihtimalle aksam indirimi
        
        deal = {
            "country": c["code"],
            "country_name": c["name"],
            "flag": c["flag"],
            "name": f"{c['flag']} {template['name']}",
            "store": f"{chain} {c['flag']}",
            "category": template["cat"],
            "originalPrice": orig_var,
            "discountedPrice": disc_var,
            "unit": template["unit"],
            "distance": f"{chain} ({dist_num} km)",
            "eveningClearance": is_evening
        }
        all_deals.append(deal)
        deal_id += 1

output_data = {
    "version": "2.0_multi_country_1000",
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_deals": len(all_deals),
    "deals": all_deals
}

with open("germany_deals.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"BASARILI: Toplam {len(all_deals)} firsat germany_deals.json dosyasina yazildi!")
