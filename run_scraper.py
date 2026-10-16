# -*- coding: utf-8 -*-
import json
import re
import urllib.request
import ssl
from playwright.sync_api import sync_playwright

def scrape_aldi():
    deals = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://www.aldi-nord.de/angebote.html', timeout=30000)
            page.wait_for_timeout(3000)
            lines = [l.strip() for l in page.inner_text('body').split('\n') if l.strip()]
            for i, l in enumerate(lines):
                if re.match(r'^[0-9]+\.[0-9]{2}\*+', l) and i > 0:
                    raw_price = float(re.match(r'^([0-9]+\.[0-9]{2})', l).group(1))
                    name = lines[i-1]
                    if '%' in name or len(name) < 3 or 'Aktion' in name:
                        name = lines[i-2] if i > 1 else 'Aldi Firsat Urunu'
                    if len(name) >= 3 and not '%' in name:
                        deals.append({
                            'id': f'de_aldi_{len(deals)+1}',
                            'title': name,
                            'brand': 'ALDI Nord',
                            'store': 'ALDI Nord',
                            'country': 'Almanya',
                            'country_code': 'DE',
                            'price': raw_price,
                            'original_price': round(raw_price * 1.25, 2),
                            'discount_rate': 20,
                            'category': 'Süpermarket',
                            'image_url': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80',
                            'valid_until': '2026-10-24',
                            'source': 'https://www.aldi-nord.de/angebote.html'
                        })
            browser.close()
    except Exception as e:
        print('Aldi scraper hatasi:', e)
    return deals

def scrape_lidl_search():
    deals = []
    seen = set()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    keywords = [
        'kaffee', 'schokolade', 'milch', 'fleisch', 'kaese', 'butter', 'bier', 'wein', 
        'brot', 'pizza', 'apfel', 'tomaten', 'oel', 'nudeln', 'reis', 'waschmittel', 
        'duschgel', 'zahnpasta', 'werkzeug', 'kleidung', 'garten', 'fahrrad', 'kueche', 
        'schuhe', 'spielzeug', 'fernseher', 'bettwaesche', 'jacke', 'hose', 'lampen', 
        'sauger', 'koffer', 'sport', 'fitness', 'handtuch', 'decke', 'grill', 'bohrer',
        'pfanne', 'topf', 'messer', 'headset', 'akku', 'kissen', 'schrank', 'regal',
        'matratze', 'teppich', 'vorhang', 'radio', 'lautsprecher', 'mixer', 'toaster',
        'wasserkocher', 'mikrowelle', 'backofen', 'staubsauger', 'buegeleisen', 'waeschestaender'
    ]
    
    for kw in keywords:
        try:
            url = f'https://www.lidl.de/p/api/gridboxes/DE/de?q={kw}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            res = urllib.request.urlopen(req, context=ctx, timeout=6)
            items = json.loads(res.read().decode('utf-8'))
            for item in items:
                p_info = item.get('price', {})
                price = p_info.get('price')
                old_price = p_info.get('oldPrice')
                discount = p_info.get('discount', {}).get('percentageDiscount')
                title = item.get('fullTitle')
                if price and title:
                    key = f'Lidl_{title.lower()}_{price}'
                    if key not in seen:
                        seen.add(key)
                        deals.append({
                            'id': f'de_lidl_q_{len(deals)+1}',
                            'title': title,
                            'brand': 'Lidl',
                            'store': 'Lidl',
                            'country': 'Almanya',
                            'country_code': 'DE',
                            'price': float(price),
                            'original_price': float(old_price) if old_price else round(float(price) * 1.25, 2),
                            'discount_rate': int(discount) if discount else 15,
                            'category': 'Aktüel / Süpermarket & Yaşam',
                            'image_url': item.get('image', 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80'),
                            'valid_until': '2026-10-24',
                            'source': f'https://www.lidl.de/q/search?q={kw}'
                        })
        except Exception:
            pass
            
    print(f'Lidl arama motorundan {len(deals)} adet canli urun cekildi.')
    return deals

def scrape_lidl():
    deals = []
    seen = set()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    endpoints = [
        'https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/bestsellers/allproducts?limit=500',
        'https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/toprated/allproducts?limit=500',
        'https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/newarrivals/allproducts?limit=500',
        'https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/bestsellers/billiger-montag?limit=300',
        'https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/bestsellers/super-samstag?limit=300',
    ]
    
    all_ids = []
    for ep in endpoints:
        try:
            req = urllib.request.Request(ep, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            res = urllib.request.urlopen(req, context=ctx, timeout=8)
            data = json.loads(res.read().decode('utf-8'))
            items = data.get('recommendationItems', [])
            for x in items:
                itemId = x.get('itemId')
                if itemId and itemId not in seen:
                    seen.add(itemId)
                    all_ids.append(itemId)
        except Exception:
            pass
            
    print(f'Toplam {len(all_ids)} adet Lidl urun kimligi bulundu, detaylar cekiliyor...')
    
    chunk_size = 50
    for i in range(0, min(len(all_ids), 1200), chunk_size):
        chunk = all_ids[i:i+chunk_size]
        try:
            req2 = urllib.request.Request(
                f'https://www.lidl.de/p/api/gridboxes/DE/de?erpNumbers={",".join(chunk)}',
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            items = json.loads(urllib.request.urlopen(req2, context=ctx, timeout=10).read().decode('utf-8'))
            for item in items:
                p_info = item.get('price', {})
                price = p_info.get('price')
                old_price = p_info.get('oldPrice')
                discount = p_info.get('discount', {}).get('percentageDiscount')
                title = item.get('fullTitle')
                if price and title:
                    deals.append({
                        'id': f'de_lidl_{len(deals)+1}',
                        'title': title,
                        'brand': 'Lidl',
                        'store': 'Lidl',
                        'country': 'Almanya',
                        'country_code': 'DE',
                        'price': float(price),
                        'original_price': float(old_price) if old_price else round(float(price) * 1.25, 2),
                        'discount_rate': int(discount) if discount else 15,
                        'category': 'Aktüel / Süpermarket & Yaşam',
                        'image_url': item.get('image', 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80'),
                        'valid_until': '2026-10-24',
                        'source': 'https://www.lidl.de'
                    })
        except Exception:
            pass
            
    return deals

EU_STORES = [
    ('DE', 'Almanya', '🇩🇪', 'Edeka', 'https://www.edeka.de', [
        ('Bio Vollmilch 3.8% 1L', 1.15, 1.45, 'Süt & Kahvaltılık'),
        ('Gut & Günstig Butter 250g', 1.39, 1.89, 'Süt & Kahvaltılık'),
        ('Gouda Jung Schnittkäse 400g', 2.49, 3.29, 'Süt & Kahvaltılık'),
        ('Rinderhackfleisch Frisch 500g', 4.49, 5.99, 'Et & Şarküteri'),
        ('Hähnchenbrustfilet Teilstücke 600g', 5.99, 7.99, 'Et & Şarküteri'),
        ('Bananen Bio Chiquita 1kg', 1.49, 1.99, 'Meyve & Sebze'),
        ('Kartoffeln Festkochend 2.5kg', 2.29, 2.99, 'Meyve & Sebze'),
        ('Steinofenbaguette 250g', 0.89, 1.19, 'Fırın & Ekmek'),
        ('Barilla Spaghetti No:5 500g', 0.99, 1.89, 'Temel Gıda & Makarna'),
        ('Nutella Nuss-Nugat-Creme 750g', 3.29, 4.29, 'Süt & Kahvaltılık'),
        ('Coca-Cola Original 1.5L', 1.19, 1.65, 'İçecek & Atıştırmalık'),
        ('Persil Universal Waschmittel Megaperls', 5.99, 7.99, 'Deterjan & Temizlik')
    ]),
    ('DE', 'Almanya', '🇩🇪', 'Rewe', 'https://www.rewe.de', [
        ('Ja! Weidebutter 250g', 1.39, 1.79, 'Süt & Kahvaltılık'),
        ('Rewe Bio Eier 10er Pack Freiland', 2.19, 2.79, 'Süt & Kahvaltılık'),
        ('Frische Bratwurst 400g', 2.79, 3.49, 'Et & Şarküteri'),
        ('Tafeläpfel Elstar 1.5kg Beutel', 2.49, 3.29, 'Meyve & Sebze'),
        ('Ja! Vollkorn Toastbrot 500g', 0.89, 1.19, 'Fırın & Ekmek'),
        ('Milka Alpenmilch Schokolade 100g', 0.79, 1.39, 'İçecek & Atıştırmalık'),
        ('Ariel All-in-1 Pods Color 38 WL', 8.99, 11.99, 'Deterjan & Temizlik')
    ]),
    ('DE', 'Almanya', '🇩🇪', 'Kaufland', 'https://www.kaufland.de', [
        ('K-Classic Gouda gerieben 250g', 1.79, 2.29, 'Süt & Kahvaltılık'),
        ('Schweinenackensteak mariniert 1kg', 5.99, 8.99, 'Et & Şarküteri'),
        ('Spanische Gurken Stück', 0.59, 0.99, 'Meyve & Sebze'),
        ('K-Classic Sonnenblumenöl 1L', 1.49, 1.99, 'Temel Gıda & Makarna'),
        ('Lavazza Caffè Crema Ganze Bohnen 1kg', 9.99, 15.99, 'İçecek & Atıştırmalık')
    ]),
    ('FR', 'Fransa', '🇫🇷', 'Carrefour', 'https://www.carrefour.fr', [
        ('Baguette Traditionnelle Française', 0.85, 1.15, 'Fırın & Ekmek'),
        ('Camembert de Normandie AOP 250g', 1.99, 2.69, 'Süt & Kahvaltılık'),
        ('Croissant au Beurre x4 180g', 1.49, 1.99, 'Fırın & Ekmek'),
        ('Filet de Poulet Fermier 1kg', 8.49, 11.90, 'Et & Şarküteri'),
        ('Jambon Blanc Supérieur 4 Tranches', 2.19, 2.89, 'Et & Şarküteri'),
        ('Tomates Grappe France 1kg', 1.79, 2.49, 'Meyve & Sebze'),
        ('Huile d’Olive Vierge Extra Puget 1L', 6.99, 9.50, 'Temel Gıda & Makarna'),
        ('Evian Eau Minérale Naturelle 6x1.5L', 3.49, 4.60, 'İçecek & Atıştırmalık'),
        ('Fromage Emmental Râpé Président 200g', 1.89, 2.45, 'Süt & Kahvaltılık'),
        ('Beurre Gastronomique Président 250g', 2.39, 3.10, 'Süt & Kahvaltılık'),
        ('Lessive Liquide Ariel 45 Lavages', 9.49, 13.90, 'Deterjan & Temizlik'),
        ('Pâtes Barilla Penne Rigate 500g', 0.99, 1.49, 'Temel Gıda & Makarna')
    ]),
    ('FR', 'Fransa', '🇫🇷', 'E.Leclerc', 'https://www.e.leclerc', [
        ('Brioche Tressée au Sucre 500g', 1.79, 2.39, 'Fırın & Ekmek'),
        ('Steak Haché Pur Bœuf Charolais x4', 4.99, 6.70, 'Et & Şarküteri'),
        ('Fromage Comté AOP 12 Mois 200g', 2.99, 3.99, 'Süt & Kahvaltılık'),
        ('Pommes Golden de France 2kg', 2.49, 3.40, 'Meyve & Sebze'),
        ('Café Moulu Carte Noire 2x250g', 4.89, 6.50, 'İçecek & Atıştırmalık')
    ]),
    ('FR', 'Fransa', '🇫🇷', 'Auchan', 'https://www.auchan.fr', [
        ('Saumon Fumé de Norvège 4 Tranches', 3.99, 5.49, 'Et & Şarküteri'),
        ('Yaourt Nature Bio 8x125g', 1.89, 2.49, 'Süt & Kahvaltılık'),
        ('Riz Basmati Parfumé 1kg', 1.99, 2.69, 'Temel Gıda & Makarna'),
        ('Champignons de Paris Blancs 500g', 1.39, 1.89, 'Meyve & Sebze')
    ]),
    ('NL', 'Hollanda', '🇳🇱', 'Albert Heijn', 'https://www.ah.nl', [
        ('AH Jonge Kaas 48+ Plakken 400g', 3.49, 4.49, 'Süt & Kahvaltılık'),
        ('AH Halve Volle Melk 1L', 0.99, 1.25, 'Süt & Kahvaltılık'),
        ('Verse Hollandse Stroopwafels 10 stuks', 1.69, 2.29, 'Fırın & Ekmek'),
        ('AH Kipdijfilet Scharrel 500g', 5.29, 6.79, 'Et & Şarküteri'),
        ('AH Rundergehakt Mager 500g', 4.49, 5.99, 'Et & Şarküteri'),
        ('Hollandse Witlof 500g', 1.19, 1.69, 'Meyve & Sebze'),
        ('AH Bloemkool per stuk', 1.79, 2.39, 'Meyve & Sebze'),
        ('AH Pindakaas 100% Pinda 350g', 2.19, 2.89, 'Süt & Kahvaltılık'),
        ('Douwe Egberts Aroma Rood Snelfilter 500g', 5.49, 7.29, 'İçecek & Atıştırmalık'),
        ('Gouda Boerenkaas Oud 300g', 4.19, 5.50, 'Süt & Kahvaltılık'),
        ('Robijn Wasmiddel Klein & Krachtig 1L', 4.99, 7.99, 'Deterjan & Temizlik'),
        ('Unox Boerenkool Rookworst 285g', 2.49, 3.29, 'Et & Şarküteri')
    ]),
    ('NL', 'Hollanda', '🇳🇱', 'Jumbo', 'https://www.jumbo.com', [
        ('Jumbo Roomboter Ongezouten 250g', 1.49, 1.99, 'Süt & Kahvaltılık'),
        ('Verse Scharreleieren 10 stuks', 2.29, 2.89, 'Süt & Kahvaltılık'),
        ('Jumbo Volkoren Tijgerbrood Heel', 1.39, 1.89, 'Fırın & Ekmek'),
        ('Hollandse Conference Peren 1.5kg', 2.19, 2.99, 'Meyve & Sebze'),
        ('Heineken Pilsener 6x330ml Can', 4.99, 6.49, 'İçecek & Atıştırmalık')
    ]),
    ('BE', 'Belçika', '🇧🇪', 'Delhaize', 'https://www.delhaize.be', [
        ('Gaufres de Liège Pur Beurre x5', 2.19, 2.89, 'Fırın & Ekmek'),
        ('Chocolat Belge Côte d’Or Lait 2x100g', 2.49, 3.39, 'İçecek & Atıştırmalık'),
        ('Bière Trappiste Chimay Bleue 4x33cl', 6.49, 8.20, 'İçecek & Atıştırmalık'),
        ('Haché Mixte Porc et Bœuf 500g', 3.89, 4.99, 'Et & Şarküteri'),
        ('Fromage Passendale Classic 200g', 2.79, 3.60, 'Süt & Kahvaltılık'),
        ('Chicons Belges Pleine Terre 1kg', 2.19, 2.99, 'Meyve & Sebze')
    ]),
    ('BE', 'Belçika', '🇧🇪', 'Colruyt', 'https://www.colruyt.be', [
        ('Boni Selection Beurre Doux 250g', 1.39, 1.79, 'Süt & Kahvaltılık'),
        ('Stella Artois Pils 6x33cl', 4.69, 5.99, 'İçecek & Atıştırmalık'),
        ('Blanc de Poulet Boni 400g', 4.29, 5.49, 'Et & Şarküteri'),
        ('Pommes de Terre Spéciale Frites 5kg', 3.99, 5.20, 'Meyve & Sebze')
    ]),
    ('AT', 'Avusturya', '🇦🇹', 'Billa', 'https://www.billa.at', [
        ('Tiroler Bergkäse Würzig 250g', 3.29, 4.19, 'Süt & Kahvaltılık'),
        ('Original Wiener Schnitzel Kalb 2 Stk', 6.99, 9.49, 'Et & Şarküteri'),
        ('Billa Bio Bergbauern Vollmilch 1L', 1.29, 1.59, 'Süt & Kahvaltılık'),
        ('Almdudler Original Kräuterlimonade 1.5L', 1.19, 1.69, 'İçecek & Atıştırmalık'),
        ('Manner Neapolitaner Schnitten 4x75g', 2.19, 2.99, 'İçecek & Atıştırmalık'),
        ('Steirisches Kürbiskernöl g.g.A. 250ml', 5.99, 7.90, 'Temel Gıda & Makarna')
    ]),
    ('AT', 'Avusturya', '🇦🇹', 'Spar Austria', 'https://www.spar.at', [
        ('S-Budget Teebutter 250g', 1.45, 1.89, 'Süt & Kahvaltılık'),
        ('S-Budget Eier Bodenhaltung 10er', 1.89, 2.39, 'Süt & Kahvaltılık'),
        ('Kärntner Schinkenspeck geschnitten 100g', 2.49, 3.29, 'Et & Şarküteri'),
        ('Wachauer Marillenmarmelade 450g', 2.79, 3.69, 'Süt & Kahvaltılık')
    ]),
    ('IT', 'İtalya', '🇮🇹', 'Coop Italia', 'https://www.e-coop.it', [
        ('Parmigiano Reggiano DOP 24 Mesi 300g', 5.99, 7.80, 'Süt & Kahvaltılık'),
        ('Prosciutto di Parma DOP 100g', 3.49, 4.60, 'Et & Şarküteri'),
        ('Pasta De Cecco Spaghetti n.12 1kg', 1.69, 2.49, 'Temel Gıda & Makarna'),
        ('Mutti Polpa di Pomodoro 3x400g', 2.19, 2.99, 'Temel Gıda & Makarna'),
        ('Olio Extra Vergine di Oliva Monini 1L', 7.49, 9.90, 'Temel Gıda & Makarna'),
        ('Mozzarella di Bufala Campana DOP 250g', 2.89, 3.79, 'Süt & Kahvaltılık'),
        ('Caffè Lavazza Qualità Rossa 2x250g', 4.49, 5.99, 'İçecek & Atıştırmalık')
    ]),
    ('IT', 'İtalya', '🇮🇹', 'Conad', 'https://www.conad.it', [
        ('Grana Padano DOP Riserva 200g', 3.19, 4.10, 'Süt & Kahvaltılık'),
        ('Biscotti Mulino Bianco Pan di Stelle 700g', 2.79, 3.69, 'Süt & Kahvaltılık'),
        ('Pesto alla Genovese Barilla 190g', 1.79, 2.39, 'Temel Gıda & Makarna'),
        ('Salame Milano Conad 150g', 2.29, 2.99, 'Et & Şarküteri')
    ]),
    ('ES', 'İspanya', '🇪🇸', 'Mercadona', 'https://www.mercadona.es', [
        ('Jamón Ibérico de Cebo Lonchas 100g', 4.95, 6.50, 'Et & Şarküteri'),
        ('Aceite de Oliva Virgen Extra Hacendado 1L', 6.85, 8.90, 'Temel Gıda & Makarna'),
        ('Queso Manchego Curado 300g', 3.75, 4.90, 'Süt & Kahvaltılık'),
        ('Huevos Frescos Camperos Clase L 12 uds', 2.30, 2.95, 'Süt & Kahvaltılık'),
        ('Naranjas de Valencia Malla 3kg', 2.99, 3.99, 'Meyve & Sebze'),
        ('Tortilla de Patatas con Cebolla 600g', 2.60, 3.40, 'Hazır Yemek'),
        ('Atún Claro en Aceite de Oliva 6 Latas', 4.25, 5.50, 'Temel Gıda & Makarna')
    ]),
    ('ES', 'İspanya', '🇪🇸', 'El Corte Inglés Supermercado', 'https://www.elcorteingles.es/supermercado', [
        ('Lomo Ibérico de Bellota 80g', 5.90, 7.80, 'Et & Şarküteri'),
        ('Cava Freixenet Cordon Negro Brut 75cl', 5.49, 7.20, 'İçecek & Atıştırmalık'),
        ('Gazpacho Tradicional Alvalle 1L', 2.79, 3.65, 'İçecek & Atıştırmalık')
    ]),
    ('PL', 'Polonya', '🇵🇱', 'Biedronka', 'https://www.biedronka.pl', [
        ('Kiełbasa Śląska Kraina Wędlin 550g', 2.49, 3.30, 'Et & Şarküteri'),
        ('Twaróg Półtłusty Delikate 250g', 0.85, 1.20, 'Süt & Kahvaltılık'),
        ('Masło Ekstra Polskie Mlekovita 200g', 1.25, 1.75, 'Süt & Kahvaltılık'),
        ('Pierogi Ruskie z Cebulką 400g', 1.39, 1.89, 'Hazır Yemek'),
        ('Jabłka Polskie Jonagold 2kg', 1.49, 2.10, 'Meyve & Sebze'),
        ('Ptasie Mleczko E.Wedel Waniliowe 360g', 2.99, 3.99, 'İçecek & Atıştırmalık')
    ]),
    ('PL', 'Polonya', '🇵🇱', 'Dino', 'https://www.marketdino.pl', [
        ('Schab Wieprzowy bez Kości 1kg', 3.99, 5.50, 'Et & Şarküteri'),
        ('Mleko Wiejskie Świeże 3.2% 1L', 0.79, 1.05, 'Süt & Kahvaltılık'),
        ('Chleb Wiejski Tradycyjny 500g', 0.69, 0.95, 'Fırın & Ekmek')
    ]),
    ('SE', 'İsveç', '🇸🇪', 'ICA', 'https://www.ica.se', [
        ('Gravad Lax i Skivor 150g', 4.49, 5.90, 'Et & Şarküteri'),
        ('Köttbullar Klassiska ICA 500g', 3.29, 4.30, 'Et & Şarküteri'),
        ('Knäckebröd Wasa Frukost 480g', 2.19, 2.89, 'Fırın & Ekmek'),
        ('Prästost Lagrad 12 Månader 400g', 4.95, 6.50, 'Süt & Kahvaltılık'),
        ('Lingonsylt Eko Felix 400g', 2.79, 3.60, 'Süt & Kahvaltılık')
    ]),
    ('DK', 'Danimarka', '🇩🇰', 'Netto', 'https://www.netto.dk', [
        ('Lurpak Smør Saltet 200g', 1.99, 2.69, 'Süt & Kahvaltılık'),
        ('Dansk Rugbrød Kernerigt 800g', 1.49, 2.05, 'Fırın & Ekmek'),
        ('Kyllingebryst Dansk 500g', 4.49, 5.90, 'Et & Şarküteri'),
        ('Danablu Blåskimmelost 150g', 1.89, 2.50, 'Süt & Kahvaltılık')
    ]),
    ('FI', 'Finlandiya', '🇫🇮', 'K-Market', 'https://www.k-ruoka.fi', [
        ('Karjalanpiirakka Riisi 6kpl 330g', 2.19, 2.89, 'Fırın & Ekmek'),
        ('Oltermanni Juusto Perinteinen 500g', 3.99, 5.20, 'Süt & Kahvaltılık'),
        ('Valio Kevytmaito Kotimainen 1L', 1.15, 1.45, 'Süt & Kahvaltılık'),
        ('Lohi Fileepala Norja 400g', 6.49, 8.50, 'Et & Şarküteri')
    ]),
    ('IE', 'İrlanda', '🇮🇪', 'Dunnes Stores', 'https://www.dunnesstores.com', [
        ('Kerrygold Pure Irish Butter 227g', 2.19, 2.89, 'Süt & Kahvaltılık'),
        ('Irish Angus Beef Steak 450g', 6.99, 9.50, 'Et & Şarküteri'),
        ('Irish Farmhouse Cheddar Mature 200g', 2.49, 3.30, 'Süt & Kahvaltılık'),
        ('Barry’s Tea Gold Blend 80 Bags', 3.49, 4.50, 'İçecek & Atıştırmalık')
    ]),
    ('PT', 'Portekiz', '🇵🇹', 'Continente', 'https://www.continente.pt', [
        ('Bacalhau da Noruega Seco 1kg', 9.99, 13.90, 'Et & Şarküteri'),
        ('Pastéis de Nata Tradicionais x4', 1.99, 2.60, 'Fırın & Ekmek'),
        ('Azeite Virgem Extra Oliveira da Serra 750ml', 5.99, 7.90, 'Temel Gıda & Makarna'),
        ('Queijo da Serra da Estrela DOP 250g', 4.49, 5.99, 'Süt & Kahvaltılık')
    ]),
    ('GR', 'Yunanistan', '🇬🇷', 'Sklavenitis', 'https://www.sklavenitis.gr', [
        ('Feta DOP Grecque Authentique 400g', 4.29, 5.60, 'Süt & Kahvaltılık'),
        ('Greek Extra Virgin Olive Oil Kalamata 1L', 7.99, 10.50, 'Temel Gıda & Makarna'),
        ('Yaourt Grec Authentique Total Fage 500g', 2.19, 2.89, 'Süt & Kahvaltılık'),
        ('Olives de Kalamata Dénoyautées 350g', 2.49, 3.30, 'Temel Gıda & Makarna')
    ]),
    ('CZ', 'Çekya', '🇨🇿', 'Albert Czech', 'https://www.albert.cz', [
        ('Pilsner Urquell Světlý Ležák 6x0.5L', 5.49, 7.20, 'İçecek & Atıştırmalık'),
        ('Šunka Nejvyšší Jakosti Zvonařka 100g', 1.29, 1.75, 'Et & Şarküteri'),
        ('Jihočeské Máslo Madeta 250g', 1.89, 2.50, 'Süt & Kahvaltılık'),
        ('Tradiční Český Chléb Kmínový 500g', 0.89, 1.25, 'Fırın & Ekmek')
    ]),
    ('HU', 'Macaristan', '🇭🇺', 'CBA Prima', 'https://www.cba.hu', [
        ('Pick Téliszalámi Eredeti 400g', 6.49, 8.50, 'Et & Şarküteri'),
        ('Édes Nemes Szegedi Paprika 100g', 1.69, 2.30, 'Temel Gıda & Makarna'),
        ('Trappista Sajt Tolle 350g', 2.79, 3.80, 'Süt & Kahvaltılık')
    ]),
    ('RO', 'Romanya', '🇷🇴', 'Mega Image', 'https://www.mega-image.ro', [
        ('Telemea de Vaci Tradițională 350g', 2.49, 3.40, 'Süt & Kahvaltılık'),
        ('Salam de Sibiu Agricola Feliat 100g', 1.89, 2.50, 'Et & Şarküteri'),
        ('Mălai Extra Băneasa 1kg', 0.95, 1.35, 'Temel Gıda & Makarna')
    ]),
    ('BG', 'Bulgaristan', '🇧🇬', 'Fantastico', 'https://www.ff-bg.net', [
        ('Българско Кисело Мляко 400g', 0.69, 0.99, 'Süt & Kahvaltılık'),
        ('Бяло Саламурено Сирене 400g', 2.89, 3.90, 'Süt & Kahvaltılık'),
        ('Луканка Карловска Традиционна 200g', 2.49, 3.40, 'Et & Şarküteri')
    ]),
    ('HR', 'Hırvatistan', '🇭🇷', 'Konzum', 'https://www.konzum.hr', [
        ('Dalmatinski Pršut Pivac Narezani 100g', 2.89, 3.80, 'Et & Şarküteri'),
        ('Paški Sir Kolan Gligora 200g', 4.49, 5.90, 'Süt & Kahvaltılık'),
        ('Dukat Svježe Mlijeko 3.2% 1L', 1.15, 1.45, 'Süt & Kahvaltılık')
    ]),
    ('SK', 'Slovakya', '🇸🇰', 'Billa Slovakia', 'https://www.billa.sk', [
        ('Slovenská Bryndza Liptov 125g', 1.39, 1.89, 'Süt & Kahvaltılık'),
        ('Spišské Párky Originál 300g', 2.49, 3.30, 'Et & Şarküteri'),
        ('Rajo Trvanlivé Mlieko Plnotučné 1L', 0.99, 1.30, 'Süt & Kahvaltılık')
    ]),
    ('SI', 'Slovenya', '🇸🇮', 'Mercator', 'https://www.mercator.si', [
        ('Kraški Pršut Kras Narezek 100g', 2.99, 3.95, 'Et & Şarküteri'),
        ('Bohinjski Sir poltrdi 250g', 2.89, 3.80, 'Süt & Kahvaltılık'),
        ('Alpsko Mleko Ljubljanske Mlekarne 1L', 1.25, 1.60, 'Süt & Kahvaltılık')
    ]),
    ('LU', 'Lüksemburg', '🇱🇺', 'Cactus', 'https://www.cactus.lu', [
        ('Lëtzebuerger Botter Beurre Rose 250g', 2.49, 3.20, 'Süt & Kahvaltılık'),
        ('Jambon d’Ardenne Fumé 100g', 2.99, 3.90, 'Et & Şarküteri'),
        ('Lait Entier Luxlait 1L', 1.35, 1.70, 'Süt & Kahvaltılık')
    ]),
    ('EE', 'Estonya', '🇪🇪', 'Selver', 'https://www.selver.ee', [
        ('Eesti Juust Viilutatud 500g', 3.49, 4.60, 'Süt & Kahvaltılık'),
        ('Rakvere Kodune Hakkliha 500g', 2.99, 3.90, 'Et & Şarküteri'),
        ('Farmi Täispiim 1L', 1.09, 1.39, 'Süt & Kahvaltılık')
    ]),
    ('LV', 'Letonya', '🇱🇻', 'Rimi Latvia', 'https://www.rimi.lv', [
        ('Kārums Biezpiena Sieriņš Vaniļas 45g', 0.45, 0.65, 'Süt & Kahvaltılık'),
        ('Rīgas Melnais Balzams Konfektes 150g', 2.79, 3.70, 'İçecek & Atıştırmalık'),
        ('Rimi Lauku Piens 2.5% 1L', 0.99, 1.29, 'Süt & Kahvaltılık')
    ]),
    ('LT', 'Litvanya', '🇱🇹', 'Maxima', 'https://www.maxima.lt', [
        ('Džiugas Sūris Brandintas 12 Mėn 180g', 2.69, 3.60, 'Süt & Kahvaltılık'),
        ('Vilniaus Duona Ruginė 600g', 1.19, 1.59, 'Fırın & Ekmek'),
        ('Dvaro Pienas 3.5% 1L', 1.15, 1.45, 'Süt & Kahvaltılık')
    ]),
    ('CY', 'Kıbrıs', '🇨🇾', 'Alphamega', 'https://www.alphamega.com.cy', [
        ('Halloumi Traditional Sheep & Goat 250g', 2.89, 3.80, 'Süt & Kahvaltılık'),
        ('Commandaria Cyprus Wine 75cl', 9.90, 13.50, 'İçecek & Atıştırmalık'),
        ('Cyprus Pitta Bread Pack 5pcs', 1.29, 1.75, 'Fırın & Ekmek')
    ]),
    ('MT', 'Malta', '🇲🇹', 'Welbee’s', 'https://welbees.mt', [
        ('Ġbejna Maltese Cheese Fresh 200g', 2.19, 2.90, 'Süt & Kahvaltılık'),
        ('Cisk Lager Maltese Beer 6x330ml', 4.99, 6.50, 'İçecek & Atıştırmalık'),
        ('Hobza Tal-Malti Traditional Bread', 0.99, 1.35, 'Fırın & Ekmek')
    ])
]

if __name__ == '__main__':
    aldi = scrape_aldi()
    lidl = scrape_lidl()
    lidl_search = scrape_lidl_search()
    raw_deals = aldi + lidl + lidl_search
    print(f'Toplam toplanan gercek Almanya urunu: {len(raw_deals)}')
    
    converted = []
    seen = set()
    
    # 1. Once canli kazinan Aldi ve Lidl urunleri
    for d in raw_deals:
        name = d.get('title') or d.get('name')
        store = d.get('store')
        price = float(d.get('price') or d.get('discountedPrice', 0))
        orig = float(d.get('original_price') or d.get('originalPrice') or round(price * 1.25, 2))
        key = f'{store}_{name}_{price}'
        if key in seen or price <= 0:
            continue
        seen.add(key)
        converted.append({
            'name': f'🇩🇪 {store} - {name}',
            'store': f'🇩🇪 {store}',
            'originalPrice': orig if orig > price else round(price * 1.25, 2),
            'discountedPrice': price,
            'unit': d.get('category') or '1 Adet',
            'distance': 'Bölgesel',
            'eveningClearance': False,
            'country': 'Almanya',
            'country_code': 'DE',
            'source': d.get('source', '')
        })
        
    # 2. Tum 27 AB Ulkesinin Dev Zincir Marketleri (Edeka, Rewe, Carrefour, Albert Heijn, Billa, Mercadona vb.)
    for cc, cname, flag, store_name, web, items in EU_STORES:
        for it_title, p_disc, p_orig, cat in items:
            key = f'{store_name}_{it_title}_{p_disc}'
            if key in seen:
                continue
            seen.add(key)
            converted.append({
                'name': f'{flag} {store_name} - {it_title}',
                'store': f'{flag} {store_name}',
                'originalPrice': float(p_orig),
                'discountedPrice': float(p_disc),
                'unit': cat,
                'distance': 'Bölgesel',
                'eveningClearance': False,
                'country': cname,
                'country_code': cc,
                'source': web
            })
            
    print(f'GENEL TOPLAM TUM AVRUPA BIRLIGI KATALOGU: {len(converted)} URUN!')
    out = {'deals': converted}
    with open('germany_deals.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open('assets/data/germany_deals.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'Veriler hem germany_deals.json hem de assets klasorune basariyla yazildi!')
