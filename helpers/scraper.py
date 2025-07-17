import requests
from bs4 import BeautifulSoup

def scrape_chrono24(url):
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        price_elem = item.select_one('.article-price')
        title_elem = item.select_one('.article-title')
        link_elem = item.select_one('a')
        if price_elem and title_elem and link_elem:
            listings.append({
                "title": title_elem.text.strip(),
                "price": price_elem.text.strip(),
                "link": link_elem['href']
            })
    return listings

        return []

    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        price_elem = item.select_one('.article-price')
        title_elem = item.select_one('.article-title')
        link_elem = item.select_one('a')
        if price_elem and title_elem and link_elem:
            listings.append({
                'title': title_elem.text.strip(),
                'price': price_elem.text.strip(),
                'link': link_elem['href']
            })
    print(f"[scraper] Parsed {len(listings)} listings")
    return listings
