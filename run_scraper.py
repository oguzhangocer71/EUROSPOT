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

if __name__ == '__main__':
    aldi = scrape_aldi()
    lidl = scrape_lidl()
    lidl_search = scrape_lidl_search()
    raw_deals = aldi + lidl + lidl_search
    print(f'Toplam toplanan gercek urun: {len(raw_deals)} (Aldi: {len(aldi)}, Lidl Bestseller: {len(lidl)}, Lidl Arama: {len(lidl_search)})')
    
    converted = []
    seen = set()
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
        
    out = {'deals': converted}
    with open('germany_deals.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open('assets/data/germany_deals.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'Veriler hem germany_deals.json hem de assets klasorune {len(converted)} adet olarak basariyla yazildi!')
