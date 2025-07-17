import os
import random
import time
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# API-based fallback for sites blocking direct scraping
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")

PROXIES = os.getenv("HTTP_PROXY", None)


def fetch_with_scrapingbee(url):
    """
    Use ScrapingBee API to fetch HTML when direct requests are blocked.
    """
    api_url = "https://app.scrapingbee.com/api/v1"
    params = {
        'api_key': SCRAPINGBEE_API_KEY,
        'url': url,
        'render_js': 'false'
    }
    resp = requests.get(api_url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.text


def scrape_chrono24(url):
    """
    Fetch listings via HTTP; fallback to ScrapingBee API on 403 or error.
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
    }
    html = None
    try:
        resp = requests.get(url, headers=headers, proxies={'http': PROXIES, 'https': PROXIES}, timeout=10)
        if resp.status_code == 403:
            raise requests.RequestException("403 Forbidden")
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        print(f"Direct HTTP fetch failed ({e}), switching to ScrapingBee fallback.")
        if not SCRAPINGBEE_API_KEY:
            print("ScrapingBee API key not configured. Returning empty list.")
            return []
        try:
            html = fetch_with_scrapingbee(url)
        except Exception as sb_err:
            print(f"ScrapingBee fetch failed: {sb_err}")
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
    return listings
