import os
import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

PROXIES = os.getenv("HTTP_PROXY", None)

def scrape_chrono24(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.google.com'
    }
    try:
        resp = requests.get(url, headers=headers, proxies={'http': PROXIES, 'https': PROXIES}, timeout=10)
        if resp.status_code == 403:
            return scrape_with_selenium(url)
        resp.raise_for_status()
    except requests.RequestException:
        return scrape_with_selenium(url)

    soup = BeautifulSoup(resp.text, 'html.parser')
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

def scrape_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/chromium'

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

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
