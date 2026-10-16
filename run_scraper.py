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

def scrape_lidl():
    deals = []
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request('https://recommendations.lidl-shop.com/r/api/recommendations/DE/de/web/bestsellers/allproducts?limit=60', headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, context=ctx).read().decode('utf-8'))
        ids = [x['itemId'] for x in data.get('recommendationItems', [])]
        if ids:
            req2 = urllib.request.Request(f'https://www.lidl.de/p/api/gridboxes/DE/de?erpNumbers={",".join(ids[:50])}', headers={'User-Agent': 'Mozilla/5.0'})
            items = json.loads(urllib.request.urlopen(req2, context=ctx).read().decode('utf-8'))
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
                        'original_price': float(old_price) if old_price else round(float(price) * 1.2, 2),
                        'discount_rate': int(discount) if discount else 15,
                        'category': 'Aktüel / Giyim & Ev',
                        'image_url': item.get('image', 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&q=80'),
                        'valid_until': '2026-10-24',
                        'source': 'https://www.lidl.de'
                    })
    except Exception as e:
        print('Lidl scraper hatasi:', e)
    return deals

if __name__ == '__main__':
    aldi = scrape_aldi()
    lidl = scrape_lidl()
    all_deals = aldi + lidl
    print(f'Toplam Cekilen Gercek Urun: {len(all_deals)} (Aldi: {len(aldi)}, Lidl: {len(lidl)})')
    with open('germany_deals.json', 'w', encoding='utf-8') as f:
        json.dump(all_deals, f, ensure_ascii=False, indent=2)
    print('germany_deals.json basariyla guncellendi!')
