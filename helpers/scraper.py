```python
import os
import random
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# Cookie to bypass cookie consent banner
COOKIES = {"cookieconsent_status": "dismiss"}


def scrape_chrono24(url):
    """
    Fetch listings via HTTP with cookie consent header.
    Returns list of dicts with 'title', 'price', 'link'.
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
    }
    try:
        resp = requests.get(url, headers=headers, cookies=COOKIES, timeout=10)
        resp.raise_for_status()
        html = resp.text
        print(f"[scraper] HTTP fetch succeeded: status={resp.status_code}, length={len(html)}")
    except requests.RequestException as e:
        print(f"[scraper] HTTP fetch failed: {e}")
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
